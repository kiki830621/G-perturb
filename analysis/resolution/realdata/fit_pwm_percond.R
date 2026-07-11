#!/usr/bin/env Rscript
# fit_pwm_percond.R  —  issue #14-B: per-condition variance-component decomposition.
#
# condition (Rest / Stim8hr / Stim48hr) is a FIXED facet, so its textbook G-theory treatment is a
# separate analysis WITHIN each level. For each activation state we fit the SAME selected estimator
# (PWM = REML crossed mixed model) restricted to that condition's obs -- condition drops out of the
# model inside a slice, leaving Target x Guide x Donor. The measurement-error floor is re-estimated
# from the NTC cells WITHIN each condition (per-condition me-removal; the activation state changes
# expression variance, so a pooled me-floor would be biased). Feeds a per-condition D-study.
#
#   env FIT_CORES (default detectCores()-2), SIGNAL_Q (default 0.90)
# Reads design.csv, effect.f32 (gene-major float32), gene_names.txt, pwm_components.csv (pooled,
#   for a fixed signal-gene set = comparable across conditions).
# Writes pwm_components_percond.csv (long: gene x cond, me-corrected) + pwm_percond_summary.json.

suppressWarnings(suppressMessages({ library(lme4); library(parallel); library(jsonlite) }))
here <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
if (length(here) == 0 || is.na(here)) here <- "analysis/resolution/realdata"

d <- read.csv(file.path(here, "design.csv"), stringsAsFactors = TRUE)
n_obs <- nrow(d)
genes <- readLines(file.path(here, "gene_names.txt")); genes <- genes[nzchar(genes)]
eff_path <- file.path(here, "effect.f32")
NCORES <- as.integer(Sys.getenv("FIT_CORES", as.character(max(1, detectCores() - 2))))
SIGNAL_Q <- as.numeric(Sys.getenv("SIGNAL_Q", "0.90"))
ctrl <- lmerControl(check.conv.singular = .makeCC("ignore", tol = 1e-4))

# signal genes: top-decile by POOLED s2_T (fixed set => comparable across the 3 conditions)
pooled <- read.csv(file.path(here, "pwm_components.csv"))
sTp <- suppressWarnings(as.numeric(pooled$s2_T))
thr <- quantile(sTp, SIGNAL_Q, na.rm = TRUE)
sig_idx0 <- which(!is.na(sTp) & sTp >= thr) - 1L      # 0-indexed gene positions into effect.f32
cat(sprintf("fit_pwm_percond: %d signal genes (s2_T>=%.4f) x 3 conditions, %d cores\n",
            length(sig_idx0), thr, NCORES))

conds <- c("Rest", "Stim8hr", "Stim48hr")
idx_c    <- setNames(lapply(conds, function(cc) which(d$cond == cc)), conds)                       # obs rows
ntc_c    <- setNames(lapply(conds, function(cc) which(d$cond == cc & d$gtype == "non-targeting")), conds)
design_c <- setNames(lapply(conds, function(cc) droplevels(d[idx_c[[cc]], ])), conds)

read_gene <- function(g) {  # 0-indexed gene -> full n_obs effect vector (gene-major float32)
  con <- file(eff_path, "rb"); on.exit(close(con))
  seek(con, where = as.double(g) * n_obs * 4, origin = "start")
  readBin(con, "numeric", n = n_obs, size = 4)
}

fit_gene_conds <- function(g) {
  y <- read_gene(g)
  do.call(rbind, lapply(conds, function(cc) {
    dc <- design_c[[cc]]; dc$y <- y[idx_c[[cc]]]
    r <- tryCatch({
      fit <- lmer(y ~ (1|target) + (1|target:guide) + (1|target:donor),   # no cond term inside a slice
                  data = dc, REML = TRUE, control = ctrl)
      vc <- as.data.frame(VarCorr(fit))
      gv <- function(grp) { x <- vc$vcov[vc$grp == grp & is.na(vc$var2)]; if (length(x)) x[1] else 0 }
      s2_res <- gv("Residual")
      s2_me  <- var(y[ntc_c[[cc]]])                    # per-condition measurement-error floor
      c(gv("target"), gv("target:guide"), gv("target:donor"), s2_res, s2_me, max(0, s2_res - s2_me))
    }, error = function(e) rep(NA_real_, 6))
    data.frame(gene = genes[g + 1L], cond = cc, s2_T = r[1], s2_TG = r[2], s2_TD = r[3],
               s2_res = r[4], s2_me = r[5], s2_res_bio = r[6])
  }))
}

t0 <- proc.time()[3]
res <- mclapply(sig_idx0, fit_gene_conds, mc.cores = NCORES, mc.preschedule = TRUE)
el <- round(proc.time()[3] - t0, 1)
DF <- do.call(rbind, res)
write.csv(DF, file.path(here, "pwm_components_percond.csv"), row.names = FALSE)

summ <- list(n_signal_genes = length(sig_idx0), conditions = conds, signal_quantile = SIGNAL_Q,
             signal_threshold_s2T = round(as.numeric(thr), 4), elapsed_s = el, cores = NCORES,
             note = "per-condition me-corrected variance components on a fixed pooled-signal gene set; feeds per-condition D-study")
for (cc in conds) {
  sub <- DF[DF$cond == cc & !is.na(DF$s2_T), ]
  summ[[cc]] <- list(n_fitted = nrow(sub),
    median_s2_T = round(median(sub$s2_T), 4), median_s2_TG = round(median(sub$s2_TG), 4),
    median_s2_TD = round(median(sub$s2_TD), 4), median_s2_res_bio = round(median(sub$s2_res_bio), 4))
}
write(toJSON(summ, auto_unbox = TRUE, pretty = TRUE), file.path(here, "pwm_percond_summary.json"))
cat(sprintf("done: %d gene x cond fits in %.0fs (%.1f min)\n", nrow(DF), el, el / 60))
cat("wrote pwm_components_percond.csv + pwm_percond_summary.json\n")
