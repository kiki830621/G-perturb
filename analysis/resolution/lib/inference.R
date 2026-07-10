# inference.R  —  task 3.1  (permutation exchange groups respect the nested/crossed structure).
#
# The measurement-error GLS second stage lives in candidates.R (me removal). This file adds the
# permutation inference contract: to test a facet component (e.g. target x guide), labels are
# reshuffled ONLY within the exchangeable stratum (guide within target), never globally — a global
# shuffle would break the nesting and inflate type-I. Provides a calibration runner for the frozen
# type_I gate ([0.04, 0.06]).

suppressWarnings(suppressMessages(library(lme4)))

# reshuffle `factor_col` within each level of `within_col` (respects nesting)
permute_within <- function(df, factor_col, within_col) {
  idx <- ave(seq_len(nrow(df)), df[[within_col]], FUN = function(i) i[sample(length(i))])
  df[[factor_col]] <- df[[factor_col]][idx]
  df
}

# TG component test statistic: REML estimate of the target:guide variance (me-removed residual
# is irrelevant to the RE variance, so we read it directly).
.tg_stat <- function(df) {
  ctrl <- lmerControl(check.conv.singular = .makeCC("ignore", tol = 1e-4))
  fit <- suppressWarnings(lmer(y ~ cond + (1|target) + (1|target:guide) + (1|target:donor),
              data = df, REML = TRUE, control = ctrl))
  vc <- as.data.frame(VarCorr(fit))
  x <- vc$vcov[vc$grp == "target:guide" & is.na(vc$var2)]; if (length(x)) x[1] else 0
}

# one permutation p-value for "is there a target x guide component?"
perm_pvalue_TG <- function(df, n_perm = 199) {
  obs <- .tg_stat(df)
  null <- vapply(seq_len(n_perm), function(b) .tg_stat(permute_within(df, "guide", "target")),
                 numeric(1))
  (1 + sum(null >= obs)) / (1 + n_perm)
}

# type-I calibration: `simulate_null` must return a data.frame drawn under the NULL (s2_TG = 0),
# taking a single integer seed. Collects permutation p-values and reports rejection rate at alpha.
# Reduced (n_data, n_perm) is a smoke; the full frozen scale (n_perm >= 5000 null) runs on cluster.
type_I_calibration <- function(simulate_null, n_data = 100, n_perm = 199, alpha = 0.05, seed0 = 1) {
  p <- vapply(seq_len(n_data), function(k) perm_pvalue_TG(simulate_null(seed0 + k), n_perm = n_perm),
              numeric(1))
  list(alpha = alpha, n_data = n_data, n_perm = n_perm,
       rejection_rate = mean(p <= alpha), mean_p = mean(p))
}
