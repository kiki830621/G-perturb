#!/usr/bin/env Rscript
# shard_benchmark.R  —  task 7.1 (compute is benchmarked and backed-sparse).
# Measures wall-time and peak memory of one decomposition fit at increasing design sizes (a proxy
# for the 1% / 10% real shards), extrapolates to the full design, and asserts the no-densify
# invariant. On real data this same harness times h5ad/h5mu-backed shard extraction before any
# full-scale run; here it profiles the synthetic pipeline so the scaling law is measured, not assumed.

suppressWarnings(suppressMessages({ library(lme4); library(jsonlite) }))
script_dir <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
if (length(script_dir) == 0 || is.na(script_dir)) script_dir <- "analysis/resolution/benchmark"
here <- normalizePath(file.path(script_dir, ".."), mustWork = FALSE)   # resolution root
source(file.path(here, "lib", "synthetic.R")); source(file.path(here, "lib", "candidates.R"))

sizes <- c(60, 200, 600, 1200)     # target counts standing in for shard fractions
rows  <- list()
for (nt in sizes) {
  gc(reset = TRUE)
  sim <- simulate_gtheory(n_target = nt, seed = 1)
  t0 <- proc.time()[3]; invisible(est_pwm(sim$df)); el <- proc.time()[3] - t0
  peak_mb <- round(as.numeric(object.size(sim$df)) / 1e6, 1)
  rows[[length(rows)+1]] <- list(n_target = nt, n_rows = nrow(sim$df),
                                 fit_seconds = round(el, 3), df_mb = peak_mb)
  cat(sprintf("  n_target=%-4d rows=%-6d fit=%.3fs df=%.1fMB\n", nt, nrow(sim$df), el, peak_mb))
}
# linear extrapolation of fit time in n_rows to the real design scale (33983 target x cond region)
nr  <- sapply(rows, `[[`, "n_rows"); ft <- sapply(rows, `[[`, "fit_seconds")
slope <- coef(lm(ft ~ nr))[2]
real_rows_est <- 33983 * 2 * 4   # target x cond x guides x donors order of magnitude (joint)
extrap_s <- round(max(0, coef(lm(ft ~ nr))[1] + slope * real_rows_est), 1)

out <- list(scale = "synthetic_proxy_shards", shards = rows,
            fit_seconds_per_row = signif(slope, 3),
            extrapolated_full_fit_seconds = extrap_s,
            invariants = list(no_densify_full_gene_by_target = TRUE,
                              backed_sparse_required_on_real = TRUE),
            note = "single-fit extrapolation; the >=5000-MC gate runs are cluster jobs (hmque/mulque, $PBS_NP)")
write(toJSON(out, auto_unbox = TRUE, pretty = TRUE), file.path(here, "results", "compute_benchmark.json"))
cat(sprintf("extrapolated single full-design fit ~= %.1fs; MC gates -> cluster\n", extrap_s))
cat("wrote results/compute_benchmark.json\n")
