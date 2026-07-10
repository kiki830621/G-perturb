# Crosswalk — `resolve-methodology-blockers` → `generalizability-decomposition` (#8) + audit unblock

Tasks 8.1 / 8.2. This maps each #8 artifact to a keep / replace / remove / add action driven by the
resolution gate outcomes, and lists the `audit-complete-methodology` → `approved` unblock conditions.

Cells that depend on the real joint pseudobulk are marked **`pending-joint`** — they resolve only
after `download/fetch_joint_pseudobulk.sh` + `manifest/build_manifest.py` land the frozen evidence
manifest (B-001). Synthetic-stage outcomes already produced this turn are filled in.

## 1. #8 artifact crosswalk

| #8 artifact | Action | Driven by | Status |
|---|---|---|---|
| `proposal.md` (h5mu-marginal, `1−CCC`, Fay–Herriot) | **replace** headline with the winning candidate + honest floor | synthetic recovery winner + identifiability | winner **pending-joint** (synthetic: PWM leads under Gaussian) |
| `design.md` §9 scalar heuristic | **keep** as sanity-check stepping-stone | unchanged reframe | keep |
| `design.md` §10.4 distribution-light core | **replace** the estimator with the selected candidate | `results/synthetic_recovery/` | **pending-joint** full verdict |
| `design.md` replication floor | **replace** with `not_identifiable` unless a lane replicate exists | `results/identifiability.json` R1 | **resolved (synthetic)**: merged pseudobulk floor = `not_identifiable` |
| `spec.md` variance-component requirements | **add** the fail-closed identifiability clauses | `lib/identifiability.R` gates | **resolved (synthetic)** |
| `tasks.md` 2.x/3.x/4.1/5.x statistical core | **replace** with the gated pipeline in `analysis/resolution/` | all gates | **pending-joint** (paused until gates pass) |
| gene-wise / pathway tasks | **add** single atlas-wide FDR tree + separated pathway nulls | `results/fdr_pathway.json` | **resolved (synthetic)**: atlas FDR within gate |
| K562 / arrayed labelling | **replace** any "validation" wording per taxonomy | `results/validation_manifest.json` | **resolved**: K562 = transportability |

## 2. Audit → `approved` unblock conditions (P0/P1 → gate result)

| Finding | Unblock condition (frozen) | Gate artifact | Status |
|---|---|---|---|
| B-001 | frozen manifest over real joint pseudobulk | `results/evidence.manifest.json` | **pending-joint** (builder ready, fail-closed) |
| B-002/B-003 | design-rank + separability fail-closed | `results/identifiability.json` | **resolved (synthetic)** |
| B-004/B-006 | type-I ∈ [0.04, 0.06] at full MC | `results/type_I_calibration.json` | smoke ok; **full → cluster** |
| B-005/B-007 | bias ≤ 0.02, coverage ∈ [0.93,0.97], winner's-curse slope ∈ [0.9,1.1] | `results/synthetic_recovery/` | bias **resolved** (PWM 0.004 Gaussian); coverage/slope **pending full** |
| B-008/B-009 | FDR ≤ 0.06, pathway nulls separated | `results/fdr_pathway.json` | **resolved (synthetic)** |
| B-010 | leak-free validation manifest, honest taxonomy | `results/validation_manifest.json` | **resolved** |
| B-011 | shard benchmark, no densify | `results/compute_benchmark.json` | **resolved (synthetic proxy)** |

**Rule (unchanged):** `audit-complete-methodology` flips to `approved` only when every row above is
`resolved` on the **real** joint pseudobulk (not synthetic proxy) and a gate-passing candidate exists.
Until then #8's statistical core stays paused, and any quantity the real design cannot identify is
reported `not_identifiable` — never fabricated.
