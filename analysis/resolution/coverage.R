#!/usr/bin/env Rscript
# coverage.R  —  task 3.1 coverage arm (spec: interval coverage of the selected method's component
# shares must fall in the frozen band [0.93, 0.97]).
#
# For the SELECTED method PWM, build a parametric-bootstrap percentile CI for each variance-component
# share and measure how often the KNOWN truth falls inside, across many synthetic datasets. Parametric
# bootstrap = simulate from the fitted model (fixed cond effect + redrawn random effects + residual +
# the known heteroscedastic measurement error), refit, percentile CI.
#
#   env COVERAGE_NDATA (default 60), COVERAGE_NBOOT (default 99), N_TARGET (default 400)
# Full frozen scale (large N x B) is a cluster job; a local parallel run is labelled by scale.

suppressWarnings(suppressMessages({ library(lme4); library(jsonlite); library(parallel) }))
here <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
if (length(here) == 0 || is.na(here)) here <- "analysis/resolution"
source(file.path(here, "lib", "synthetic.R"))
gates <- fromJSON(file.path(here, "results", "gates.frozen.json"))$payload$thresholds$interval_coverage
NCORES <- as.integer(Sys.getenv("RECOVERY_CORES", as.character(max(1, detectCores() - 2))))
ctrl <- lmerControl(check.conv.singular = .makeCC("ignore", tol = 1e-4))
comps <- c("T","TG","TD","res")

# PWM absolute variance components (unweighted REML + measurement-error removal, boundary-aware)
pwm_comp <- function(df) {
  fit <- lmer(y ~ cond + (1|target) + (1|target:guide) + (1|target:donor),
              data = df, REML = TRUE, control = ctrl)
  vc <- as.data.frame(VarCorr(fit))
  g <- function(grp) { x <- vc$vcov[vc$grp == grp & is.na(vc$var2)]; if (length(x)) x[1] else 0 }
  res <- max(0, g("Residual") - mean(df$me_var))
  list(v = c(T = g("target"), TG = g("target:guide"), TD = g("target:donor"), res = res),
       fixed_pred = predict(fit, re.form = NA))
}
shares <- function(v) { v <- pmax(0, v); v / sum(v) }

# redraw y on df's fixed design using component variances `v` (parametric-bootstrap DGP)
redraw_y <- function(df, v, fixed_pred) {
  tg <- interaction(df$target, df$guide, drop = TRUE)
  td <- interaction(df$target, df$donor, drop = TRUE)
  a_t  <- rnorm(nlevels(df$target),      0, sqrt(v["T"]))[df$target]
  b_tg <- rnorm(nlevels(tg),             0, sqrt(v["TG"]))[tg]
  c_td <- rnorm(nlevels(td),             0, sqrt(v["TD"]))[td]
  e    <- rnorm(nrow(df),                0, sqrt(v["res"]))
  me   <- rnorm(nrow(df),                0, sqrt(df$me_var))
  fixed_pred + a_t + b_tg + c_td + e + me
}

one_dataset <- function(k) {
  sim <- simulate_gtheory(n_target = n_target, dist = "gaussian", seed = 5000 + k)
  df <- sim$df; truth <- shares(sim$meta$components[c("s2_T","s2_TG","s2_TD","s2_res")])
  names(truth) <- comps
  fit0 <- tryCatch(pwm_comp(df), error = function(e) NULL); if (is.null(fit0)) return(NULL)
  # parametric bootstrap
  boot <- matrix(NA_real_, nboot, length(comps), dimnames = list(NULL, comps))
  for (b in seq_len(nboot)) {
    dfb <- df; dfb$y <- redraw_y(df, fit0$v, fit0$fixed_pred)
    fb <- tryCatch(pwm_comp(dfb)$v, error = function(e) NULL)
    if (!is.null(fb)) boot[b, ] <- shares(fb)
  }
  ci <- apply(boot, 2, quantile, probs = c(0.025, 0.975), na.rm = TRUE)
  covered <- truth >= ci[1, ] & truth <= ci[2, ]
  as.integer(covered)
}

nd    <- as.integer(Sys.getenv("COVERAGE_NDATA", "60"))
nboot <- as.integer(Sys.getenv("COVERAGE_NBOOT", "99"))
n_target <- as.integer(Sys.getenv("N_TARGET", "400"))
scale_lbl <- if (nd >= 500 && nboot >= 199) "full" else "smoke_reduced_mc"

cat(sprintf("coverage: n_data=%d n_boot=%d n_target=%d cores=%d scale=%s\n",
            nd, nboot, n_target, NCORES, scale_lbl))
t0 <- proc.time()[3]
res <- mclapply(seq_len(nd), one_dataset, mc.cores = NCORES)
el <- round(proc.time()[3] - t0, 1)
res <- res[!vapply(res, is.null, logical(1))]
M <- do.call(rbind, res)
cov_by <- colMeans(M); cov_overall <- mean(M)

out <- list(scale = scale_lbl, n_data = nrow(M), n_boot = nboot, n_target = n_target,
            nominal = gates$nominal, accept_band = c(gates$accept_lo, gates$accept_hi),
            coverage_by_component = as.list(round(cov_by, 4)),
            coverage_overall = round(cov_overall, 4),
            within_band = (min(cov_by) >= gates$accept_lo && max(cov_by) <= gates$accept_hi),
            verdict = if (scale_lbl != "full") "smoke_only_not_a_gate_pass"
                      else if (min(cov_by) >= gates$accept_lo && max(cov_by) <= gates$accept_hi) "PASS" else "FAIL",
            elapsed_s = el)
write(toJSON(out, auto_unbox = TRUE, pretty = TRUE), file.path(here, "results", "coverage.json"))
cat(sprintf("  coverage by component: %s\n", paste(sprintf("%s=%.3f", comps, cov_by), collapse = " ")))
cat(sprintf("  band [%.2f,%.2f] -> %s  [%.0fs]\n", gates$accept_lo, gates$accept_hi, out$verdict, el))
