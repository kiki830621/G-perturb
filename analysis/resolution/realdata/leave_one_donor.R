#!/usr/bin/env Rscript
# leave_one_donor.R  —  task 6.3 last control: leave-one-donor-out stability of the decomposition.
# On the top-N genes by me-corrected share_T (where reliability matters), re-fit PWM dropping each
# donor in turn; collect per-gene share_T per holdout; rank-correlate the per-gene share_T vectors
# across holdouts. Frozen control: rank-correlation across donor holdouts >= 0.8.
#
#   env TOPN (default 500), FIT_CORES

suppressWarnings(suppressMessages({ library(lme4); library(parallel); library(jsonlite) }))
here <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
if (length(here) == 0 || is.na(here)) here <- "analysis/resolution/realdata"
d <- read.csv(file.path(here, "design.csv"), stringsAsFactors = TRUE)
n_obs <- nrow(d)
genes <- readLines(file.path(here, "gene_names.txt")); genes <- genes[nzchar(genes)]
NCORES <- as.integer(Sys.getenv("FIT_CORES", as.character(max(1, detectCores() - 2))))
TOPN <- as.integer(Sys.getenv("TOPN", "500"))
ctrl <- lmerControl(check.conv.singular = .makeCC("ignore", tol = 1e-4))

# top-N genes by me-corrected share_T
mc <- read.csv(file.path(here, "pwm_components_meCorrected.csv"))
mc <- mc[!is.na(mc$share_T), ]
top_genes <- mc$gene[order(-mc$share_T)][seq_len(min(TOPN, nrow(mc)))]
gidx <- match(top_genes, genes) - 1L                       # 0-indexed positions in effect.f32
donors <- levels(d$donor)
cat(sprintf("leave-one-donor-out: top %d genes x %d donor holdouts, %d cores\n",
            length(gidx), length(donors), NCORES))

read_gene <- function(g) {
  con <- file(file.path(here, "effect.f32"), "rb"); on.exit(close(con))
  seek(con, where = as.double(g) * n_obs * 4, origin = "start")
  readBin(con, "numeric", n = n_obs, size = 4)
}
share_T_for <- function(g, keep) {
  y <- read_gene(g)
  tryCatch({
    dd <- d[keep, ]; dd$y <- y[keep]
    fit <- lmer(y ~ cond + (1|target) + (1|target:guide) + (1|target:donor),
                data = dd, REML = TRUE, control = ctrl)
    vc <- as.data.frame(VarCorr(fit)); gv <- function(gr){x<-vc$vcov[vc$grp==gr & is.na(vc$var2)]; if(length(x))x[1] else 0}
    v <- c(gv("target"), gv("target:guide"), gv("target:donor"), gv("Residual")); v[1]/sum(v)
  }, error = function(e) NA_real_)
}

# full-data share_T (from me-corrected, for reference) + per-holdout
holdout_shares <- list()
for (dn in donors) {
  keep <- d$donor != dn
  s <- unlist(mclapply(gidx, function(g) share_T_for(g, keep), mc.cores = NCORES))
  holdout_shares[[dn]] <- s
  cat(sprintf("  dropped %s: median share_T=%.3f (n=%d)\n", dn, median(s, na.rm=TRUE), sum(!is.na(s))))
}
M <- do.call(cbind, holdout_shares)
# pairwise Spearman rank-correlation across holdouts
cc <- suppressWarnings(cor(M, method = "spearman", use = "pairwise.complete.obs"))
offdiag <- cc[upper.tri(cc)]
min_rho <- min(offdiag, na.rm = TRUE); med_rho <- median(offdiag, na.rm = TRUE)

out <- list(control = "leave_one_donor_out", scale = "real_data_top_genes", top_n = length(gidx),
            n_donors = length(donors),
            pairwise_spearman = as.list(round(offdiag, 4)),
            min_rank_corr = round(min_rho, 4), median_rank_corr = round(med_rho, 4),
            stable = (min_rho >= 0.8),
            note = "per-gene share_T rank-correlation across donor holdouts on top-signal genes; frozen threshold 0.8")
write(toJSON(out, auto_unbox = TRUE, pretty = TRUE), file.path(here, "leave_one_donor.json"))
cat(sprintf("min rank-corr across donor holdouts = %.3f (median %.3f) -> stable=%s\n",
            min_rho, med_rho, min_rho >= 0.8))
cat("wrote leave_one_donor.json\n")
