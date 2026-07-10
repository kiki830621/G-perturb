#!/usr/bin/env Rscript
# synthetic_recovery.R  —  task 6.2 ("Method selection uses synthetic recovery only").
#
# Pre-registered: reads the FROZEN gates, runs each candidate over many synthetic datasets with
# KNOWN variance components, measures component-recovery bias/RMSE, and issues a per-candidate
# verdict against the frozen component_recovery gate. Method selection is by synthetic loss ONLY.
#
#   env RECOVERY_REPS  (default 150)  number of synthetic datasets per scenario
# Full pre-registered scale is gates$thresholds$monte_carlo$power_reps_min (>=2000): run on the
# Academia Sinica cluster (see benchmark/). A local reduced-rep run is a HARNESS SMOKE and is
# labelled as such in the output (`scale`), never reported as a passed full-scale gate.

suppressWarnings(suppressMessages({ library(jsonlite) }))
here <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
if (length(here) == 0 || is.na(here)) here <- "analysis/resolution"
source(file.path(here, "lib", "synthetic.R"))
source(file.path(here, "lib", "candidates.R"))

res_dir <- file.path(here, "results")
gates   <- fromJSON(file.path(res_dir, "gates.frozen.json"))$payload$thresholds
reps     <- as.integer(Sys.getenv("RECOVERY_REPS", "150"))
n_target <- as.integer(Sys.getenv("N_TARGET", "600"))   # design scale; rmse gate is calibrated here
full_reps <- gates$monte_carlo$power_reps_min
# rmse precision is design-scale dependent (~1/sqrt(n_target)); the frozen rmse gate assumes the
# real many-target design, so a "full" verdict also requires a realistic n_target.
realistic_scale <- n_target >= 400L
scale_lbl <- if (reps >= full_reps && realistic_scale) "full" else "smoke_reduced_mc"

bias_max <- gates$component_recovery$bias_abs_max
rmse_max <- gates$component_recovery$rmse_max
comps    <- c("T","TG","TD","res")

scenarios <- list(
  gaussian = list(dist = "gaussian"),
  heavy    = list(dist = "heavy")
)

cat(sprintf("synthetic recovery: reps=%d/scenario  n_target=%d  scale=%s  (full needs reps>=%d & n_target>=400)\n",
            reps, n_target, scale_lbl, full_reps))

summary_all <- list()
for (sc in names(scenarios)) {
  dist <- scenarios[[sc]]$dist
  # accumulators: per candidate, matrix reps x components of (est - truth)
  err <- lapply(names(CANDIDATES), function(x) matrix(NA_real_, reps, length(comps),
                                                     dimnames = list(NULL, comps)))
  names(err) <- names(CANDIDATES)
  neg_ct <- setNames(integer(length(CANDIDATES)), names(CANDIDATES))
  fail_ct <- setNames(integer(length(CANDIDATES)), names(CANDIDATES))

  t0 <- proc.time()[3]
  for (r in seq_len(reps)) {
    sim <- simulate_gtheory(n_target = n_target, dist = dist, seed = r)
    truth <- sim$truth[comps]
    for (nm in names(CANDIDATES)) {
      out <- CANDIDATES[[nm]](sim$df)
      if (!isTRUE(out$ok) || any(is.na(out$shares))) { fail_ct[nm] <- fail_ct[nm] + 1; next }
      err[[nm]][r, ] <- out$shares[comps] - truth
      if (isTRUE(out$neg)) neg_ct[nm] <- neg_ct[nm] + 1
    }
  }
  el <- round(proc.time()[3] - t0, 1)

  for (nm in names(CANDIDATES)) {
    E <- err[[nm]]; E <- E[stats::complete.cases(E), , drop = FALSE]
    bias <- colMeans(E)
    rmse <- sqrt(colMeans(E^2))
    max_abs_bias <- max(abs(bias)); max_rmse <- max(rmse)
    pass <- (max_abs_bias <= bias_max) && (max_rmse <= rmse_max) && (scale_lbl == "full")
    verdict <- if (scale_lbl != "full") "smoke_only_not_a_gate_pass"
               else if (pass) "PASS" else "FAIL"
    summary_all[[length(summary_all) + 1]] <- list(
      scenario = sc, candidate = nm, scale = scale_lbl, reps_effective = nrow(E),
      bias = as.list(round(bias, 4)), rmse = as.list(round(rmse, 4)),
      max_abs_bias = round(max_abs_bias, 4), max_rmse = round(max_rmse, 4),
      gate = list(bias_abs_max = bias_max, rmse_max = rmse_max),
      negative_component_reps = unname(neg_ct[nm]), fit_failures = unname(fail_ct[nm]),
      verdict = verdict, elapsed_s = el)
    cat(sprintf("  [%s] %-32s bias=%.3f rmse=%.3f neg=%d fail=%d -> %s\n",
                sc, nm, max_abs_bias, max_rmse, neg_ct[nm], fail_ct[nm], verdict))
  }
}

# candidate-disagreement diagnostic (frozen trigger)
disagree <- local({
  gauss <- Filter(function(x) x$scenario == "gaussian", summary_all)
  sh <- sapply(gauss, function(x) x$max_rmse)
  if (length(sh) >= 2) max(sh) - min(sh) else NA
})
out <- list(
  frozen_gates_sha256 = fromJSON(file.path(res_dir, "gates.frozen.json"))$sha256,
  scale = scale_lbl, reps = reps, n_target = n_target, full_reps_required = full_reps,
  rmse_gate_note = "rmse precision is design-scale dependent (~1/sqrt(n_target)); frozen rmse_max assumes the real many-target design",
  selection_rule = "primary = min synthetic loss among gate-passing candidates; external validation never enters",
  candidate_disagreement = list(value = round(disagree, 4),
                                trigger_gt = gates$candidate_disagreement$trigger_gt),
  results = summary_all)
write(toJSON(out, auto_unbox = TRUE, pretty = TRUE, digits = 6, null = "null"),
      file.path(res_dir, "synthetic_recovery", "recovery_summary.json"))
cat(sprintf("\nwrote results/synthetic_recovery/recovery_summary.json (scale=%s)\n", scale_lbl))
