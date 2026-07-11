#!/usr/bin/env Rscript
# fit_pwm.R  —  issue #11 Phase 2: fit the SELECTED method (PWM = REML crossed mixed model) per gene
# on the real NTC-relative effect, in parallel. This is the actual selected estimator on real data
# (not the rejected KDP SS-sweep). Variance components -> per-gene variance shares.
#
#   env FIT_CORES (default detectCores()-2)
# Reads realdata/effect.f32 (gene-major float32), realdata/design.csv, realdata/gene_names.txt.
# Writes realdata/pwm_components.csv (one row per gene) + realdata/pwm_summary.json (profile-level).

suppressWarnings(suppressMessages({ library(lme4); library(parallel); library(jsonlite) }))
here <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
if (length(here) == 0 || is.na(here)) here <- "analysis/resolution/realdata"

d <- read.csv(file.path(here, "design.csv"), stringsAsFactors = TRUE)
n_obs <- nrow(d)
genes <- readLines(file.path(here, "gene_names.txt")); genes <- genes[nzchar(genes)]
n_gene <- length(genes)
eff_path <- file.path(here, "effect.f32")
NCORES <- as.integer(Sys.getenv("FIT_CORES", as.character(max(1, detectCores() - 2))))
ctrl <- lmerControl(check.conv.singular = .makeCC("ignore", tol = 1e-4))
cat(sprintf("fit_pwm: %d genes x %d obs, %d cores\n", n_gene, n_obs, NCORES))

read_gene <- function(g) {  # 0-indexed gene -> its effect vector (float32 gene-major)
  con <- file(eff_path, "rb"); on.exit(close(con))
  seek(con, where = as.double(g) * n_obs * 4, origin = "start")
  readBin(con, "numeric", n = n_obs, size = 4)
}

fit_one <- function(g) {
  y <- read_gene(g)
  out <- tryCatch({
    dd <- d; dd$y <- y
    fit <- lmer(y ~ cond + (1|target) + (1|target:guide) + (1|target:donor),
                data = dd, REML = TRUE, control = ctrl)
    vc <- as.data.frame(VarCorr(fit))
    gv <- function(grp) { x <- vc$vcov[vc$grp == grp & is.na(vc$var2)]; if (length(x)) x[1] else 0 }
    v <- c(T = gv("target"), TG = gv("target:guide"), TD = gv("target:donor"), res = gv("Residual"))
    s <- v / sum(v)
    c(v, s_T = s["T"], s_TG = s["TG"], s_TD = s["TD"], s_res = s["res"])
  }, error = function(e) rep(NA_real_, 8))
  out
}

t0 <- proc.time()[3]
res <- mclapply(seq_len(n_gene) - 1L, fit_one, mc.cores = NCORES, mc.preschedule = TRUE)
el <- round(proc.time()[3] - t0, 1)
M <- do.call(rbind, res)
colnames(M) <- c("s2_T","s2_TG","s2_TD","s2_res","share_T","share_TG","share_TD","share_res")
df <- data.frame(gene = genes, M)
ok <- !is.na(df$s2_T)
write.csv(df, file.path(here, "pwm_components.csv"), row.names = FALSE)

# profile-level summary: distribution of the true-signal share (share_T) across genes
qs <- function(x) as.list(round(quantile(x, c(.05,.25,.5,.75,.95), na.rm = TRUE), 4))
summ <- list(
  n_genes = n_gene, n_fitted = sum(ok), fit_failures = sum(!ok), elapsed_s = el, cores = NCORES,
  share_T_quantiles  = qs(df$share_T[ok]),
  share_TG_quantiles = qs(df$share_TG[ok]),
  share_TD_quantiles = qs(df$share_TD[ok]),
  share_res_quantiles= qs(df$share_res[ok]),
  median_shares = list(T = round(median(df$share_T[ok]), 4), TG = round(median(df$share_TG[ok]), 4),
                       TD = round(median(df$share_TD[ok]), 4), res = round(median(df$share_res[ok]), 4)),
  note = "share_res includes measurement error (n_cells); me-removal is a documented refinement. Floor = not_identifiable (manifest).")
write(toJSON(summ, auto_unbox = TRUE, pretty = TRUE), file.path(here, "pwm_summary.json"))
cat(sprintf("fitted %d/%d genes in %.0fs (%.1f min)\n", sum(ok), n_gene, el, el/60))
cat(sprintf("  median shares: T=%.3f TG=%.3f TD=%.3f res=%.3f\n",
            median(df$share_T[ok]), median(df$share_TG[ok]), median(df$share_TD[ok]), median(df$share_res[ok])))
cat("wrote pwm_components.csv + pwm_summary.json\n")
