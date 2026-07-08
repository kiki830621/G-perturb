## Context

`docs/design.md` is the project's canonical method spec (read by issues #2 / #3 / #5 and the eventual manuscript). It currently leads with the `E_t × R_dep,t × Q_t` heuristic as if that were the shippable object. The owner's actual publication target is the full crossed variance-component / generalizability decomposition, and the Gaussian random-effects assumption is the weak link: the response is a ~10,282-gene profile (not a scalar; the §10.3 coherence gap) and DE z-scores are heavy-tailed. The data are the released summary statistics whose structure was characterized in #7 (`DE_stats.h5ad` = aggregate targets×genes + pre-computed reliability; `by_guide.h5mu` = `guide_1`/`guide_2`; `by_donors.h5mu` = 6 overlapping C(4,2) donor-pair modalities). `mac-benchmark` (`kiki830621/mac-benchmark`) is a structural template for a specs-vs-idiosyncrasy decomposition, but its variance-component core is Gaussian REML on a scalar response, so the profile-native non-parametric core is the part being added here. This change is greenfield: no modeling code exists yet.

## Goals / Non-Goals

**Goals:**

- Re-anchor the deliverable to a **distribution-light generalizability decomposition** and ship a hackathon cut by **July 13** that is real and trustworthy.
- Produce, from the released summary statistics: the design-level facet variance shares, an irreducible replication floor, per-target shrunk dependability with intervals, and a Gaussian REML baseline for contrast.
- Re-weight `docs/design.md` and update `analysis/data/DATA_AND_ASSUMPTIONS.md` to reflect the new deliverable and the h5mu-are-core download scope.
- Feed the outputs into the `#5` demo export contract.

**Non-Goals:**

- The profile-native novel non-parametric estimator, rigorous overlap-aware permutation theory, and the multivariate coherence formalization — these are the **post-hackathon paper**.
- Re-processing the ~22M cells or fetching the ~1.6 TB cell-level files.
- The full manuscript, and any claim that the estimator is "distribution-free" (that word is reserved for the replication floor).

## Decisions

### Decision 1: The headline is the design-level G-study; per-target dependability is a shrunk view

The deliverable is two coupled objects. The **headline** is the design-level G-study: facet variance shares (guide / donor / condition / target × interactions) plus an irreducible idiosyncrasy floor — "the size and structure of what the facets cannot explain." Per-target `R_dep,t` is a **shrunk view** that feeds the ranking and typology, not the headline. Alternative considered: leading with 33k per-target fits — rejected because it reorients all compute + the demo around per-target estimates and buries the atlas-level result that is the actual scientific claim.

### Decision 2: Distance-based permutational decomposition is primary; Gaussian REML is a baseline comparator

Primary estimator = a distance-based / permutational decomposition on the gene-expression profiles (dissimilarity per target-pair, facet-attributable dispersion, permutation inference) plus a **replication floor** proved by dispersion among identical-spec replicates (assumption-free). A Gaussian crossed REML on a scalar summary is fit and **shipped alongside as a baseline comparator** (mac-benchmark posture: Gaussian core wrapped in distribution-free reporting). Alternatives considered: (a) robust / heavy-tailed Bayesian (Student-t / horseshoe) — kept as the fallback if the primary stalls, but heavier and still parametric; (b) Gaussian REML as the primary — rejected because it forces the scalar reduction and the normality assumption this change exists to drop.

### Decision 3: Fay-Herriot moment-based empirical Bayes reconciles per-target shrinkage with non-normality

Per-target estimates are noisy (2 guides / 4 donors), so cross-target pooling is unavoidable. Reconcile it with non-normality via **moment-based / Fay-Herriot empirical Bayes** on the per-target distance statistics: a per-target point estimate plus its measured sampling variance (from the permutation null / within-target dispersion) drives precision-weighted shrinkage toward the pooled design-level value. This is distribution-light (moments + an optionally-robust linking), not Gaussian REML. Alternative considered: full-Bayes hierarchical — richer but heavier and reintroduces a parametric prior; deferred to the paper.

### Decision 4: The donor facet is split-half generalizability, not a one-way effect over four donors

The release exposes donors only as **disjoint-split-half correlations** (`donor_correlation_all_mean` = mean over the three ways to split four donors into two disjoint pairs) and **overlapping C(4,2)=6 pair modalities**. Model donor generalization as split-half agreement (Spearman-Brown-projectable to "all four"), or use the six pair modalities as replicate units with an overlap-respecting null. A naive `σ²_donor` over four individual levels misreads the design and is rejected. Donor generalizability is donor-panel consistency, never population generalization (four donors).

### Decision 5: The hackathon cut uses established methods only; the novel estimator is out of scope

The July 13 cut is buildable with off-the-shelf methods (distance decomposition, method-of-moments / Fay-Herriot, permutation, Gaussian REML) — no new estimator invented under deadline. Concretely: (i) design-level decomposition, (ii) replication floor, (iii) FH/EB shrinkage for a first per-target `R_dep`, (iv) §13 criterion validation **if** the validation CSVs are fetched (see Risks — the arrayed `Th1Th2` table is missing per #7), (v) the `#5` demo, with Gaussian REML as the baseline. The profile-native distance estimator, rigorous overlap-aware permutation, and the coherence formalization are Non-Goals (the paper).

### Decision 6: Terminology — "distribution-light / assumption-lean", with "distribution-free" reserved for the floor

Name the deliverable a "distribution-light / assumption-lean generalizability decomposition." Reserve "distribution-free" for the assumption-free replication floor only. Rationale: the estimator still uses moment / linking assumptions; calling the whole thing "distribution-free" overclaims (this is exactly `mac-benchmark`'s honest posture).

## Implementation Contract

**Observable behavior**: a reference implementation reads the downloaded released summary statistics (`DE_stats.h5ad` + `by_guide.h5mu` + `by_donors.h5mu`) and emits four artifacts — (a) a **facet variance-shares table** (guide / donor / condition / target × interactions, as fractions or octaves of the total), (b) a **replication floor** scalar (dispersion among identical-spec replicate profiles), (c) **per-target shrunk `R_dep,t` with intervals** (Fay-Herriot / EB), and (d) the **Gaussian REML baseline decomposition** for contrast.

**Data shape**: outputs conform to the `#5` export contract (`site/public/data/*.json` + `figures/*.svg`) so the demo consumes them without a live backend. At minimum: a variance-shares record, a floor scalar, a per-target `R_dep` table with CI, and — when available — the reliability→replication validation statistic.

**Failure modes**: single-guide targets (guide reliability undefined) are handled as a QC covariate / donor fallback, never silently dropped or zeroed. If the arrayed `Th1Th2` criterion table is unavailable (the #7 gap), criterion validation degrades to `K562`-only and is **marked as partial**, never fabricated. Negative moment-based variance components are truncated at zero and reported (or avoided by using the non-negative distance shares).

**Acceptance criteria**: the reference implementation runs end-to-end on the downloaded files and produces (a)–(d); the Gaussian baseline either agrees with the distance-based shares within a stated tolerance or the divergence is reported; the outputs pass a schema/existence check analogous to `analysis/data/validate_codebook.py`; the `#5` demo can render the variance-shares figure + the floor + the per-target view from the exported artifacts.

**Scope boundaries**: in scope = the six decisions' hackathon cut. Out of scope = the novel profile-native estimator, overlap-aware permutation theory, the coherence formalization, and the manuscript.

## Risks / Trade-offs

- [Distance decomposition over 33,983 targets × 10,282 genes is compute-heavy] → restrict to hit-gene subsets and/or use the released correlation fields as a first pass; if still heavy, the Academia Sinica statistics-institute compute (PC cluster / GPU) is available.
- [Overlapping donor pairs violate permutation independence] → use the disjoint split-half correlations the release already computes for the cut; overlap-aware permutation is Non-Goals.
- [The §13 arrayed criterion table (`Th1Th2_validation_summary`) is missing on S3 and by name in the companion repo (#7)] → criterion validation may be `K562`-only for the cut; mark it partial, do not fabricate the arrayed leg.
- [Method-of-moments variance components can go negative] → truncate at zero and report, or prefer the distance-based shares (non-negative by construction).
- [Scope creep into the paper under deadline] → the Non-Goals boundary and Decision 5 bound the cut.

## Migration Plan

Greenfield analysis — no deploy / rollback surface. The reframe edits `docs/design.md`, `analysis/data/DATA_AND_ASSUMPTIONS.md`, and `README.md`; rollback is a git revert of those edits. The retired heuristic is kept in the design as the labelled sanity-check stepping-stone, not deleted, so nothing downstream breaks silently.

## Open Questions — resolved at the 2026-07 apply checkpoint

- **Language: R-primary for the statistics** (`vegan::adonis2` distance decomposition, `lme4::lmer` Gaussian baseline, hand-rolled moment-based Fay–Herriot), `jsonlite` export. **I/O deviation**: the h5→matrix extraction stays in **Python `h5py`** (already working; reading the 46 GB h5mu in R would need Bioconductor `zellkonverter`/`rhdf5` + basilisk — too heavy under deadline). `sae` and `relaimpo` are **not needed for the cut** (FH is hand-rolled; importance-under-collinearity is a paper nicety). R env confirmed: `vegan` / `lme4` / `jsonlite` present.
- **Dissimilarity metric: `1 − CCC`** (Lin's concordance — agreement in magnitude, de-confounds effect scale, matches design §8). Pearson kept only as a secondary diagnostic. Gaussian-baseline scalar summary fixed at build time (leading-effect-direction projection or effect-norm).
- **Companion-repo CSVs: fetched** (task 1.1) — `K562_comparison` + `guide_kd_efficiency` are in `analysis/data/raw/`. `Th1Th2_validation_summary` confirmed unavailable (404 on S3, absent by name in the companion repo) → criterion validation is **K562-only, marked partial**.
- **Tractability: per-target facet distances, not a global matrix.** The design-level decomposition is `1−CCC(guide_1, guide_2)` per target and `1−CCC` across donor split-halves per target, aggregated into facet variance shares — **never** a global 33,983² distance matrix (~35 GB, infeasible).

## Resume note (apply checkpoint, 2026-07)

4/13 tasks done (1.1, 1.2, 6.1, 6.2 — the reframe landed in `docs/design.md` / `README.md` / `analysis/data/DATA_AND_ASSUMPTIONS.md`; commit `3410fc2`). The remaining 9 (2.x / 3.x / 4.1 / 5.x = the statistical core) are deferred to a dedicated session. Resume with `/spectra-apply generalizability-decomposition` (next task = index 3 = task 2.1). Suggested first slice: the Python extractor + the replication floor + per-target guide/donor `1−CCC` — the cheapest, highest-signal pieces that also give #5's demo its first real numbers.
