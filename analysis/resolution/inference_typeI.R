#!/usr/bin/env Rscript
# inference_typeI.R  —  task 3.1: type-I calibration of the nested-respecting permutation test.
#   env TYPEI_NDATA (default 25), TYPEI_NPERM (default 59)  — reduced = smoke; full -> cluster.
suppressWarnings(suppressMessages(library(jsonlite)))
here <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
if (length(here) == 0 || is.na(here)) here <- "analysis/resolution"
source(file.path(here, "lib", "synthetic.R"))
source(file.path(here, "lib", "inference.R"))
gates <- fromJSON(file.path(here, "results", "gates.frozen.json"))$payload$thresholds$type_I

ndata <- as.integer(Sys.getenv("TYPEI_NDATA", "25"))
nperm <- as.integer(Sys.getenv("TYPEI_NPERM", "59"))
full_null <- fromJSON(file.path(here, "results", "gates.frozen.json"))$payload$thresholds$monte_carlo$null_reps_min
scale_lbl <- if (nperm >= full_null && ndata >= 1000) "full" else "smoke_reduced_mc"

sim_null <- function(seed) simulate_gtheory(n_target = 60, s2_TG = 0, dist = "gaussian", seed = seed)$df
cat(sprintf("type-I calibration: n_data=%d n_perm=%d scale=%s (full needs n_perm>=%d)\n",
            ndata, nperm, scale_lbl, full_null))
t0 <- proc.time()[3]
cal <- type_I_calibration(sim_null, n_data = ndata, n_perm = nperm, alpha = gates$target)
cal$elapsed_s <- round(proc.time()[3] - t0, 1)
cal$scale <- scale_lbl
cal$accept_band <- c(gates$accept_lo, gates$accept_hi)
cal$within_band <- (cal$rejection_rate >= gates$accept_lo && cal$rejection_rate <= gates$accept_hi)
cal$verdict <- if (scale_lbl != "full") "smoke_only_not_a_gate_pass" else
               if (cal$within_band) "PASS" else "FAIL"
write(toJSON(cal, auto_unbox = TRUE, pretty = TRUE), file.path(here, "results", "type_I_calibration.json"))
cat(sprintf("  rejection_rate=%.3f (target %.2f, band [%.2f,%.2f])  -> %s  [%.1fs]\n",
            cal$rejection_rate, gates$target, gates$accept_lo, gates$accept_hi, cal$verdict, cal$elapsed_s))
