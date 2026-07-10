#!/usr/bin/env Rscript
# validation_manifest.R  —  task 5.1 (leak-free validation manifest + honest external-evidence taxonomy).
# Emits results/validation_manifest.json: declares which sources are TUNING vs HOLDOUT, classifies
# every external source by claim-bounded taxonomy, and provides a leak-check that any tuning source
# is never labelled untouched validation.

suppressWarnings(suppressMessages(library(jsonlite)))
here <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
if (length(here) == 0 || is.na(here)) here <- "analysis/resolution"

sources <- list(
  list(id = "cd4_joint_pseudobulk", role = "primary_analysis", used_for_tuning = TRUE,
       taxonomy = "internal", allowed_claim = "the estimand itself (in-sample decomposition)"),
  list(id = "synthetic_recovery",   role = "method_selection", used_for_tuning = TRUE,
       taxonomy = "internal", allowed_claim = "method selection + calibration (pre-registered)"),
  list(id = "cd4_pathway_same_data", role = "secondary_sensitivity", used_for_tuning = FALSE,
       taxonomy = "internal_sensitivity", allowed_claim = "sensitivity, NOT independent validation"),
  list(id = "k562_comparison",       role = "external", used_for_tuning = FALSE,
       taxonomy = "cross_cell_type_transportability", allowed_claim = "transportability, NOT T-cell replication"),
  list(id = "arrayed_bulk_flow",     role = "external", used_for_tuning = FALSE,
       taxonomy = "assay_translation", allowed_claim = "assay translation"),
  list(id = "t_cell_replicate_lane", role = "holdout_if_available", used_for_tuning = FALSE,
       taxonomy = "t_cell_replication", allowed_claim = "independent T-cell replication (only if a true replicate lane exists)")
)

# leak check: a source marked used_for_tuning must NOT be labelled untouched validation
leak_violations <- Filter(function(s) isTRUE(s$used_for_tuning) &&
                            grepl("validation", s$allowed_claim, ignore.case = TRUE) &&
                            !grepl("NOT", s$allowed_claim), sources)

manifest <- list(
  rule = "any source informing thresholds/weights/model-selection is TUNING and cannot be cited as untouched validation; independent claims require a reserved holdout or a separate source",
  taxonomy_legend = list(
    internal = "same CD4 data / synthetic — in-sample or method-selection, never validation",
    internal_sensitivity = "same CD4 data, different analysis — sensitivity only",
    cross_cell_type_transportability = "K562 etc. — transportability, not replication",
    assay_translation = "arrayed bulk/flow — assay translation",
    t_cell_replication = "true independent T-cell replicate lane — the only 'independent replication' claim"),
  sources = sources,
  leak_check = list(violations = length(leak_violations), clean = length(leak_violations) == 0)
)
write(toJSON(manifest, auto_unbox = TRUE, pretty = TRUE), file.path(here, "results", "validation_manifest.json"))
cat(sprintf("validation manifest: %d sources, leak_violations=%d (clean=%s)\n",
            length(sources), length(leak_violations), length(leak_violations) == 0))
cat("  K562 -> cross_cell_type_transportability (NOT independent replication)\n")
cat("wrote results/validation_manifest.json\n")
