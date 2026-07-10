# analysis/resolution/ — paper-grade empirical resolution pipeline

Implements the `resolve-methodology-blockers` OpenSpec change (Refs #9 / #10): the follow-on
programme that resolves the audit's P0/P1 blockers on real evidence, per the `CLAUDE.md`
paper-grade standard. Nothing here is a hackathon cut; a gate that has not passed on the real
joint pseudobulk is reported as such, never faked.

## Two tiers

- **Synthetic-only** (runs now, no 44.6 GB needed): freeze gates, synthetic recovery, identifiability
  fail-closed, permutation type-I, §8 controls, FDR/pathway, validation manifest, compute benchmark.
- **Real-data-gated** (runs once B-001 lands the joint pseudobulk): the same harness over the real
  grid, at full Monte-Carlo scale, on the Academia Sinica cluster.

## Run order

```bash
Rscript gates/freeze_gates.R                 # 6.1  pre-registration (write-once, checksummed)
Rscript identifiability_report.R             # 2.1/2.2  fail-closed identifiability
Rscript synthetic_recovery.R                 # 6.2  method selection by synthetic loss  (N_TARGET, RECOVERY_REPS)
Rscript inference_typeI.R                    # 3.1  nested permutation type-I  (TYPEI_NDATA, TYPEI_NPERM)
Rscript controls.R                           # 6.3  §8 controls
Rscript fdr_pathway.R                        # 4.1  atlas-wide FDR tree + pathway nulls
Rscript validation_manifest.R                # 5.1  leak-free validation + taxonomy
Rscript benchmark/shard_benchmark.R          # 7.1  compute benchmark
# --- real data ---
JOINT_URL=<url> DEST=<cluster> download/fetch_joint_pseudobulk.sh   # 1.1
python3 manifest/build_manifest.py --joint <file>                   # 1.2  (fail-closed without data)
```

Full-scale gate runs (`RECOVERY_REPS>=2000 N_TARGET>=400`, `TYPEI_NPERM>=5000`) go to the cluster
(`hmque`/`mulque`, `$PBS_NP`). A local reduced run is labelled `smoke_reduced_mc` in its output and
is never reported as a passed full-scale gate.

## File → task → finding

| Path | Task | Findings |
|---|---|---|
| `gates/freeze_gates.R` → `results/gates.frozen.json` | 6.1 | §7/§8 pre-registration |
| `lib/synthetic.R`, `lib/candidates.R`, `synthetic_recovery.R` | 6.2, 3.1/3.2 | B-002/B-005; method selection |
| `lib/identifiability.R`, `identifiability_report.R` | 2.1/2.2 | B-002/B-003 |
| `lib/inference.R`, `inference_typeI.R` | 3.1 | B-004/B-006 |
| `controls.R` → `results/controls/` | 6.3 | §8 controls |
| `fdr_pathway.R` | 4.1 | B-008/B-009 |
| `validation_manifest.R` | 5.1 | B-010 |
| `benchmark/shard_benchmark.R` | 7.1 | B-011 |
| `download/fetch_joint_pseudobulk.sh` | 1.1 | B-001 |
| `manifest/build_manifest.py` | 1.2 | B-001 |
| `CROSSWALK_to_issue8.md` | 8.1/8.2 | #8 handoff + audit unblock |

`results/*.json` are the tracked evidence (small). Large intermediates and logs are gitignored.
