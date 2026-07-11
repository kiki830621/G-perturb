# Crosswalk — `resolve-methodology-blockers` → `generalizability-decomposition` (#8) + audit unblock

Tasks 8.1 / 8.2. This maps each #8 artifact to a keep / replace / remove / add action driven by the
resolution gate outcomes, and lists the `audit-complete-methodology` → `approved` unblock conditions.

Cells that depend on the real joint pseudobulk are marked **`pending-joint`** — they resolve only
after `download/fetch_joint_pseudobulk.sh` + `manifest/build_manifest.py` land the frozen evidence
manifest (B-001). Synthetic-stage outcomes already produced this turn are filled in.

## 1. #8 artifact crosswalk

| #8 artifact | Action | Driven by | Status |
|---|---|---|---|
| `proposal.md` (h5mu-marginal, `1−CCC`, Fay–Herriot) | **replace** headline with the winning candidate + honest floor | synthetic recovery winner + identifiability | **method selected: PWM** (full synthetic recovery, only candidate PASSing both scenarios; KDP/RHF FAIL). Real-data application **pending-joint** |
| `design.md` §9 scalar heuristic | **keep** as sanity-check stepping-stone | unchanged reframe | keep |
| `design.md` §10.4 distribution-light core | **replace** the estimator with the selected candidate | `results/synthetic_recovery/` | **pending-joint** full verdict |
| `design.md` replication floor | **replace** with `not_identifiable` unless a lane replicate exists | `results/evidence.manifest.json` | **resolved on real joint**: floor = `not_identifiable` (every target×guide×donor×cond spec has exactly one row; run is not a replicate) |
| `spec.md` variance-component requirements | **add** the fail-closed identifiability clauses | `lib/identifiability.R` gates | **resolved (synthetic)** |
| `tasks.md` 2.x/3.x/4.1/5.x statistical core | **replace** with the gated pipeline in `analysis/resolution/` | all gates | **pending-joint** (paused until gates pass) |
| gene-wise / pathway tasks | **add** single atlas-wide FDR tree + separated pathway nulls | `results/fdr_pathway.json` | **resolved (synthetic)**: atlas FDR within gate |
| K562 / arrayed labelling | **replace** any "validation" wording per taxonomy | `results/validation_manifest.json` | **resolved**: K562 = transportability |

## 2. Audit → `approved` unblock conditions (P0/P1 → gate result)

| Finding | Unblock condition (frozen) | Gate artifact | Status |
|---|---|---|---|
| B-001 | frozen manifest over real joint pseudobulk | `results/evidence.manifest.json` | **resolved**: 44.6 GB downloaded + verified; manifest frozen (sha256 `aa6d03dd`); grid 44.7% complete |
| B-002/B-003 | design-rank + separability fail-closed | `results/{identifiability,evidence.manifest}.json` | **resolved on real joint**: TG/TD/TC identifiable (96–97%), floor `not_identifiable` (max_rep=1), run×donor `partially_confounded` |
| B-004/B-006 | type-I ∈ [0.04, 0.06] at full MC | `results/type_I_calibration.json` | smoke ok; **full → cluster** |
| B-005/B-007 | bias ≤ 0.02, coverage ∈ [0.93,0.97], winner's-curse slope ∈ [0.9,1.1] | `results/{synthetic_recovery,coverage}.json` | bias/RMSE **resolved at full MC** (PWM PASS both: 0.001/0.005 bias, 0.025/0.045 rmse); **coverage in-band** (N=500/B=99: T/TG/TD/res = 0.954/0.942/0.952/0.938, all ∈ [0.93,0.97]); winner's-curse slope **not yet implemented**; frozen-full coverage (N=2000/B=199) → cluster |
| B-008/B-009 | FDR ≤ 0.06, pathway nulls separated | `results/fdr_pathway.json` | **resolved (synthetic)** |
| B-010 | leak-free validation manifest, honest taxonomy | `results/validation_manifest.json` | **resolved** |
| B-011 | shard benchmark, no densify | `results/compute_benchmark.json` | **resolved (synthetic proxy)** |

**Rule (unchanged):** `audit-complete-methodology` flips to `approved` only when every row above is
`resolved` on the **real** joint pseudobulk (not synthetic proxy) and a gate-passing candidate exists.
Until then #8's statistical core stays paused, and any quantity the real design cannot identify is
reported `not_identifiable` — never fabricated.
