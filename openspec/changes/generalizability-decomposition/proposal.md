## Why

The project's published deliverable was drifting toward a reliability-weighted re-ranking heuristic (`E_t × R_dep,t × Q_t`), but the actual publication target is the full crossed variance-component / generalizability decomposition — and its Gaussian random-effects assumption is the weak link, because the response is a ~10,282-gene profile (not a scalar) and the DE z-scores are heavy-tailed. This change re-anchors the deliverable to a distribution-light generalizability decomposition and scopes a hackathon-shippable cut (due July 13) distinct from the paper-scale novel estimator.

## What Changes

- **BREAKING** Retire `E_t × R_dep,t × Q_t` as the headline; make the design-level G-study (facet variance shares over guide / donor / condition / target × interactions, plus an irreducible idiosyncrasy floor) the headline deliverable. Per-target `R_dep,t` becomes a shrunk view that feeds the ranking and typology (this re-scopes what #2 and #3 deliver).
- Adopt a distribution-light method: a distance-based / permutational decomposition on the gene-expression profiles plus a replication floor as the primary estimator; a Gaussian crossed REML on a scalar summary as a baseline comparator shipped alongside; robust / heavy-tailed Bayesian kept as the alternative if the primary stalls.
- Reconcile per-target shrinkage with non-normality via moment-based / Fay–Herriot empirical Bayes on the per-target distance statistics (measured sampling variance drives precision-weighted shrinkage toward the pooled design-level value) — not Gaussian REML.
- Model the donor facet as split-half generalizability (the release gives disjoint-split-half correlations and overlapping C(4,2) pair modalities), not a one-way random effect over four individual donors.
- Re-weight the design document (heuristic demoted to a sanity-check stepping-stone; the hierarchical / decomposition section becomes the deliverable; criterion validation becomes corroboration) and update the data-and-assumptions download-scope decision (the two per-facet h5mu files are now core inputs, not MVP-optional).
- Terminology: name the deliverable a "distribution-light / assumption-lean generalizability decomposition"; reserve "distribution-free" for the assumption-free replication floor only.

## Capabilities

### New Capabilities

- `generalizability-decomposition`: from the released CD4+ T cell Perturb-seq summary statistics, compute the design-level G-study (facet variance shares plus an irreducible idiosyncrasy floor) and per-target shrunk dependability, distribution-light, with a Gaussian REML baseline comparator reported alongside.

### Modified Capabilities

(none)

## Impact

- Affected specs: new `generalizability-decomposition`.
- Affected code:
  - New: analysis/ decomposition reference implementation plus diagnostic scripts (exact layout fixed in design.md); results/ tables and figures.
  - Modified: docs/design.md (re-weight the heuristic, hierarchical, and criterion-validation sections; add the distribution-light formulation), analysis/data/DATA_AND_ASSUMPTIONS.md (download-scope decision), README.md (deliverable statement).
  - Removed: (none)
- Affected issues: re-scopes #2 (scalar ranking to a view), #3 (per-domain profile to a view), #5 (demo headline); builds on #7 (data characterization).
