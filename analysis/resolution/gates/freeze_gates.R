#!/usr/bin/env Rscript
# freeze_gates.R  —  task 6.1  (spec: "Falsification gates are frozen before any real result")
#
# Pre-registration artifact. Writes the §7 falsification thresholds and §8 controls to
# results/gates.frozen.json with a checksum over the *threshold payload only* (so the file is
# reproducible and tamper-evident). WRITE-ONCE: if a frozen file already exists with a different
# payload, we refuse to overwrite and instead append an audit-trail entry — a post-freeze change
# must be deliberate and recorded, per the spec ("Any post-freeze change ... SHALL leave an audit
# trail") and CLAUDE.md paper-grade standard.
#
# Threshold values are transcribed from docs/reviews/sol-pass-b-adversarial-statistical-review.md §7.

suppressWarnings(suppressMessages({
  library(jsonlite)
  library(digest)
}))

here    <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
if (length(here) == 0 || is.na(here)) here <- "analysis/resolution/gates"
res_dir <- normalizePath(file.path(here, "..", "results"), mustWork = FALSE)
dir.create(res_dir, showWarnings = FALSE, recursive = TRUE)
out     <- file.path(res_dir, "gates.frozen.json")
audit   <- file.path(res_dir, "gates.audit.log")

# ---- §7 falsification gates (numeric unblock-conditions, one per finding class) -------------
thresholds <- list(
  monte_carlo = list(
    null_reps_min  = 5000L,   # type-I / FDR calibration
    power_reps_min = 2000L    # power / recovery
  ),
  type_I          = list(target = 0.05, accept_lo = 0.04, accept_hi = 0.06),   # B-004/B-006
  fdr             = list(target = 0.05, accept_hi = 0.06),                     # B-008
  false_sign_rate = list(accept_hi = 0.01),                                    # B-008
  interval_coverage = list(nominal = 0.95, accept_lo = 0.93, accept_hi = 0.97),# B-005/B-007
  component_recovery = list(bias_abs_max = 0.02, rmse_max = 0.05),             # B-002/B-005
  winners_curse   = list(slope_lo = 0.90, slope_hi = 1.10),                    # B-005 shrinkage calibration
  d_study         = list(monotone_in_reps = TRUE),                            # D-study sanity
  candidate_disagreement = list(trigger_gt = 0.05),                           # B-003 diagnosis trigger
  compute         = list(shard_benchmark_required = TRUE,
                         densify_full_matrix_forbidden = TRUE)                # B-011
)

# ---- §8 controls (must all pass on real data before a method is primary) --------------------
controls <- list(
  ntc_vs_ntc      = "NTC-vs-NTC null must fall within type_I accept band",        # B-004
  guide_cross_fit = "held-out-guide effect estimates stable within component_recovery band", # B-003
  leave_one_donor_out = "ranking rank-correlation across donor holdouts >= 0.8",  # B-003/B-007
  common_support  = "condition contrasts restricted to R2-verified common support" # B-002 selection
)

payload <- list(
  schema_version = "1.0",
  source         = "docs/reviews/sol-pass-b-adversarial-statistical-review.md#7",
  findings_covered = paste0("B-", sprintf("%03d", 1:11)),
  candidates = c("precision_weighted_multivariate",
                 "kernel_distance_permutational",
                 "robust_hierarchical_functional"),
  selection_rule = "primary method chosen ONLY by synthetic-recovery loss among gate-passing candidates; external validation never enters selection",
  fail_closed = "any quantity not identifiable from the real joint design is reported not_identifiable, never fabricated",
  thresholds = thresholds,
  controls   = controls
)

# checksum over the canonical payload only (stable across re-runs)
canonical <- toJSON(payload, auto_unbox = TRUE, digits = 12, null = "null")
checksum  <- digest(canonical, algo = "sha256", serialize = FALSE)

frozen <- list(payload = payload, sha256 = checksum)

append_audit <- function(msg) {
  cat(sprintf("%s  %s\n", format(Sys.time(), "%Y-%m-%dT%H:%M:%S%z"), msg),
      file = audit, append = TRUE)
}

if (file.exists(out)) {
  prev <- fromJSON(out, simplifyVector = FALSE)
  if (identical(prev$sha256, checksum)) {
    append_audit(sprintf("re-run: payload unchanged (sha256=%s) — no-op", substr(checksum, 1, 12)))
    cat(sprintf("Gates already frozen and unchanged (sha256=%s). No-op.\n", substr(checksum, 1, 12)))
    quit(status = 0)
  } else {
    append_audit(sprintf("REFUSED overwrite: existing sha256=%s != new sha256=%s (write-once)",
                         substr(prev$sha256, 1, 12), substr(checksum, 1, 12)))
    stop("gates.frozen.json exists with a DIFFERENT payload. Freeze is write-once. ",
         "A deliberate change must edit this script and remove the old frozen file with a recorded reason. ",
         "See gates.audit.log.")
  }
}

write(toJSON(frozen, auto_unbox = TRUE, pretty = TRUE, digits = 12, null = "null"), out)
# also write the checksum sidecar
write(checksum, file.path(res_dir, "gates.frozen.json.sha256"))
append_audit(sprintf("FROZEN sha256=%s (%d findings, %d candidates)",
                     substr(checksum, 1, 12), length(payload$findings_covered),
                     length(payload$candidates)))
cat(sprintf("Froze §7 gates + §8 controls -> %s\n  sha256 = %s\n", out, checksum))
