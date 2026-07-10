#!/usr/bin/env Rscript
# identifiability_report.R  —  tasks 2.1 / 2.2.
# Runs the fail-closed identifiability gates across four design regimes and writes
# results/identifiability.json. Demonstrates that the gates DOWNGRADE (not fabricate) exactly
# where the real data would: marginal h5mu -> TG not_identifiable; merged pseudobulk with one row
# per spec -> replication floor not_identifiable; run-aliased donor -> not separable.

suppressWarnings(suppressMessages(library(jsonlite)))
here <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
if (length(here) == 0 || is.na(here)) here <- "analysis/resolution"
source(file.path(here, "lib", "synthetic.R"))
source(file.path(here, "lib", "identifiability.R"))

terms <- list(T = "target", TG = c("target","guide"), TD = c("target","donor"),
              TGD = c("target","guide","donor"))

# --- Regime 1: JOINT design, one row per (t,g,d,c) — the merged pseudobulk case ---------------
joint  <- simulate_gtheory(n_target = 30, seed = 1)$df

# --- Regime 2: JOINT with a lane replicate (two rows per spec) --------------------------------
withrep <- rbind(cbind(joint, lane = 1L), cbind(joint, lane = 2L))

# --- Regime 3: MARGINAL over guide (h5mu-style: guide aggregated away) ------------------------
marg <- aggregate(y ~ target + donor + cond, data = joint, FUN = mean)
marg$guide <- factor(1)                    # single realized guide level -> TG must be not_identifiable
marg$me_var <- 1

# --- Regime 4: donor perfectly aliased with a sequencing run ----------------------------------
runaliased <- joint; runaliased$run <- runaliased$donor    # run == donor exactly

report <- list(
  regime_1_merged_pseudobulk = list(
    describe = "joint design, one row per target-guide-donor-cond (the real merged pseudobulk)",
    design_rank = design_rank_gate(joint, terms),
    replication_floor = replication_floor_gate(joint)),
  regime_2_lane_replicate = list(
    describe = "joint design plus a second lane per spec",
    design_rank = design_rank_gate(withrep, terms),
    replication_floor = replication_floor_gate(withrep)),
  regime_3_marginal_over_guide = list(
    describe = "guide aggregated away (h5mu marginal product)",
    design_rank = design_rank_gate(marg, terms[c("T","TG","TD")])),
  regime_4_run_aliased_donor = list(
    describe = "sequencing run perfectly aliased with donor",
    separability = separability_gate(runaliased, "donor", "run"))
)

write(toJSON(report, auto_unbox = TRUE, pretty = TRUE, null = "null"),
      file.path(here, "results", "identifiability.json"))

# console summary
cat("identifiability gates (fail-closed):\n")
cat(sprintf("  R1 merged pseudobulk : TG=%s  floor=%s\n",
            report$regime_1_merged_pseudobulk$design_rank$term_status$TG,
            report$regime_1_merged_pseudobulk$replication_floor$status))
cat(sprintf("  R2 lane replicate    : floor=%s (max_rep=%d)\n",
            report$regime_2_lane_replicate$replication_floor$status,
            report$regime_2_lane_replicate$replication_floor$max_replicate))
cat(sprintf("  R3 marginal-over-guide: TG=%s (guide has <2 realized levels)\n",
            report$regime_3_marginal_over_guide$design_rank$term_status$TG))
cat(sprintf("  R4 run-aliased-donor : donor~run=%s\n",
            report$regime_4_run_aliased_donor$separability$status))
cat("wrote results/identifiability.json\n")
