#!/usr/bin/env Rscript
# controls.R  —  task 6.3 (§8 controls). Four falsification controls; each writes results/controls/*.json.
# Controls that only need the design structure are smoke-tested on synthetic data now; those that
# need real NTC / real donor lanes run identically on the joint pseudobulk once B-001 lands.

suppressWarnings(suppressMessages({ library(lme4); library(jsonlite) }))
here <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
if (length(here) == 0 || is.na(here)) here <- "analysis/resolution"
source(file.path(here, "lib", "synthetic.R")); source(file.path(here, "lib", "candidates.R"))
outdir <- file.path(here, "results", "controls"); dir.create(outdir, showWarnings = FALSE, recursive = TRUE)
gates <- fromJSON(file.path(here, "results", "gates.frozen.json"))$payload$thresholds
ctrl <- lmerControl(check.conv.singular = .makeCC("ignore", tol = 1e-4))

tg_var <- function(df) { fit <- suppressWarnings(lmer(y ~ cond + (1|target) + (1|target:guide) + (1|target:donor),
                          data = df, REML = TRUE, control = ctrl))
  vc <- as.data.frame(VarCorr(fit)); x <- vc$vcov[vc$grp=="target:guide" & is.na(vc$var2)]; if (length(x)) x[1] else 0 }

# ---- Control 1: NTC-vs-NTC — split a null population in half; a genuine method finds ~no signal --
ntc_vs_ntc <- function(reps = 60, n_perm = 79, alpha = gates$type_I$target, seed0 = 100) {
  source(file.path(here, "lib", "inference.R"), local = TRUE)
  p <- vapply(seq_len(reps), function(k) {
    sim <- simulate_gtheory(n_target = 40, s2_T = 0, s2_TG = 0, s2_TD = 0, dist = "gaussian", seed = seed0 + k)$df
    perm_pvalue_TG(sim, n_perm = n_perm)
  }, numeric(1))
  rr <- mean(p <= alpha)
  list(control = "ntc_vs_ntc", scale = "smoke_reduced_mc", reps = reps, n_perm = n_perm,
       rejection_rate = round(rr, 3), accept_band = c(gates$type_I$accept_lo, gates$type_I$accept_hi),
       within_band = (rr >= gates$type_I$accept_lo && rr <= gates$type_I$accept_hi),
       note = "full scale (n_perm>=5000, real NTC targets) runs on the joint pseudobulk")
}

# ---- Control 2: guide cross-fit — estimate target effects on one guide, check on the held-out guide --
guide_cross_fit <- function(reps = 100, seed0 = 200) {
  cors <- vapply(seq_len(reps), function(k) {
    sim <- simulate_gtheory(n_target = 120, n_guide = 2, dist = "gaussian", seed = seed0 + k)$df
    m <- tapply(sim$y, list(sim$target, sim$guide), mean)
    suppressWarnings(cor(m[,1], m[,2], use = "complete.obs"))
  }, numeric(1))
  list(control = "guide_cross_fit", scale = "synthetic", reps = reps,
       mean_cross_guide_cor = round(mean(cors, na.rm = TRUE), 3),
       stable = mean(cors, na.rm = TRUE) >= 0.5,
       note = "held-out-guide target means should correlate; low correlation flags guide-driven artifacts")
}

# ---- Control 3: leave-one-donor-out — target ranking should be stable across donor holdouts --------
leave_one_donor_out <- function(seed = 300, n_target = 120, n_donor = 4) {
  sim <- simulate_gtheory(n_target = n_target, n_donor = n_donor, dist = "gaussian", seed = seed)$df
  rank_full <- rank(tapply(sim$y, sim$target, mean))
  taus <- vapply(levels(sim$donor), function(d) {
    sub <- sim[sim$donor != d, ]
    r <- rank(tapply(sub$y, sub$target, mean))
    suppressWarnings(cor(rank_full, r, method = "spearman"))
  }, numeric(1))
  list(control = "leave_one_donor_out", scale = "synthetic", n_donor = n_donor,
       min_rank_spearman = round(min(taus), 3), mean_rank_spearman = round(mean(taus), 3),
       stable = min(taus) >= 0.8,
       note = "ranking rank-correlation across donor holdouts >= 0.8 (frozen control)")
}

# ---- Control 4: common-support — condition contrasts only where targets overlap in support ---------
common_support <- function(seed = 400) {
  sim <- simulate_gtheory(n_target = 100, n_cond = 3, dist = "gaussian", seed = seed)$df
  # per condition, which targets are observed; contrast valid only on the intersection
  by_cond <- split(as.character(sim$target), sim$cond)
  inter <- Reduce(intersect, by_cond); uni <- Reduce(union, by_cond)
  list(control = "common_support", scale = "synthetic",
       n_targets_intersection = length(inter), n_targets_union = length(uni),
       support_fraction = round(length(inter)/max(1,length(uni)), 3),
       note = "condition contrasts restricted to the R2-verified common support; real data may drop cells")
}

results <- list(ntc_vs_ntc = ntc_vs_ntc(), guide_cross_fit = guide_cross_fit(),
                leave_one_donor_out = leave_one_donor_out(), common_support = common_support())
for (nm in names(results))
  write(toJSON(results[[nm]], auto_unbox = TRUE, pretty = TRUE), file.path(outdir, paste0(nm, ".json")))

cat("§8 controls:\n")
cat(sprintf("  ntc_vs_ntc         : rr=%.3f within_band=%s (smoke)\n", results$ntc_vs_ntc$rejection_rate, results$ntc_vs_ntc$within_band))
cat(sprintf("  guide_cross_fit    : cor=%.3f stable=%s\n", results$guide_cross_fit$mean_cross_guide_cor, results$guide_cross_fit$stable))
cat(sprintf("  leave_one_donor_out: min_tau=%.3f stable=%s\n", results$leave_one_donor_out$min_rank_spearman, results$leave_one_donor_out$stable))
cat(sprintf("  common_support     : support_frac=%.3f\n", results$common_support$support_fraction))
cat("wrote results/controls/*.json\n")
