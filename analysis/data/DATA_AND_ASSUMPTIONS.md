# Data & assumptions — released CD4+ T cell Perturb-seq

A readable narrative on top of [`CODEBOOK.json`](./CODEBOOK.json): what the released data actually
is, which of it the analysis needs to download, and the statistical assumptions the reliability
framework rests on. Written to answer three questions before any computation ([#7](https://github.com/kiki830621/G-perturb/issues/7)):

1. what is the data,
2. do we need to download all of it, and
3. what are the statistical assumptions.

This document is **descriptive**. It *lists* the assumptions and points to where each is handled in
[`docs/design.md`](../../docs/design.md); whether each assumption actually *holds* in the data is the
analysis's job ([#2](https://github.com/kiki830621/G-perturb/issues/2)), not this doc.

Structural facts below were confirmed by a read-only `h5py` inspection of the downloaded files and by
the official `raw/data_sharing_readme.md`; the "what is available" facts come from an authoritative S3
bucket listing and the companion GitHub repo's file tree.

---

## 1. Two sources, not one

| Source | What it serves | Access |
|---|---|---|
| **S3 bucket** `s3://genome-scale-tcell-perturb-seq/marson2025_data/` | the cell-level h5ad, the three genome-wide DE products, the pseudobulk h5ad, and **3** supplementary CSVs | public, no credentials; HTTPS mirror used by `fetch_data.sh` |
| **Companion GitHub** `emdann/GWT_perturbseq_analysis_2025` (`metadata/suppl_tables/`) | **all the other** supplementary tables — including the criterion-validation and knockdown-efficiency tables | public repo |

The dataset is Zhu et al. (2025), *Genome-scale Perturb-seq in primary human CD4+ T cells*, bioRxiv
`2025.12.23.696273` (Marson & Pritchard labs). Genome-wide CRISPRi, ~22M primary human CD4+ T cells,
**4 donors** (`CE0006864`, `CE0008162`, `CE0008678`, `CE0010866`) × **3 conditions** (`Rest`,
`Stim8hr`, `Stim48hr`). The four donor IDs are visible as the `by_donors.h5mu` modality names.

---

## 2. What is released (product map)

Confirmed against the S3 bucket listing and the companion-repo tree.

| Product | Where | Size | Downloaded? | Role here |
|---|---|---|---|---|
| `GWCD4i.DE_stats.h5ad` | S3 | 16.8 GB | ✅ | **the MVP file** — aggregate per-target DE + pre-computed reliability |
| `GWCD4i.DE_stats.by_guide.h5mu` | S3 | 29 GB | ✅ | per-guide-resolved vectors (guide facet) |
| `GWCD4i.DE_stats.by_donors.h5mu` | S3 | 17 GB | ✅ | per-donor-pair-resolved vectors (donor facet) |
| `DE_stats.suppl_table.csv` | S3 | 4.8 MB | ✅ | reduced 16-col flat table (no reliability fields) |
| `sample_metadata.suppl_table.csv` | S3 | 3 KB | ✅ | donor / condition / demographics map |
| `sgrna_library_metadata.suppl_table.csv` | S3 | 9.9 MB | ✅ | guide → gene, off-target geometry |
| `data_sharing_readme.md` | S3 | 26 KB | ✅ | official field dictionary |
| `K562_comparison.suppl_table.csv` | **companion repo** | small | ❌ | §13 cross-cell-type criterion (`logfc_pearson_r`) |
| `guide_kd_efficiency.suppl_table.csv` | **companion repo** | small | ❌ | §11 knockdown covariate (`t_statistic`, `signif_knockdown`) |
| `Th1Th2_validation_summary.suppl_table.csv` | **not found** (see §4) | — | ❌ | §13 arrayed bulk+flow criterion — **name/location unresolved** |
| `GWCD4i.pseudobulk_merged.h5ad` | S3 | large | ❌ | guide×donor×condition pseudobulk (`n_vars=18,129`) — not needed |
| `D*_*.assigned_guide.h5ad` ×12 | S3 | ~1.6 TB | ❌ **never** | raw cell-level counts — out of scope |

---

## 3. The three DE-stats products, structurally

All three share the **same** `.obs` (27 columns) and `.var` (`gene_ids`, `gene_name`) schema and the
**same 6 `.layers`** (`log_fc`, `zscore`, `lfcSE`, `baseMean`, `p_value`, `adj_p_value`), each a
`targets × genes` matrix of DESeq2 statistics. They differ only in *what a row's effect is resolved
over*:

| Product | Object of a row | `n_obs` | genes | Modalities |
|---|---|---|---|---|
| `DE_stats.h5ad` | (target × condition), **guides + donors aggregated** | 33,983 | 10,282 | — (plain AnnData) |
| `by_guide.h5mu` | (target × condition), **one guide** | `guide_1`: 33,488 · `guide_2`: 26,078 | 10,282 | `guide_1`, `guide_2` |
| `by_donors.h5mu` | (target × condition), **one donor-pair** | 4,880 per pair | 10,273 | 6 pairs = C(4,2) |

Notes that matter for the analysis:

- **`guide_2` has 7,410 fewer rows than `guide_1`** (26,078 vs 33,488): those are **single-guide
  targets** — present only in `guide_1`, so their cross-guide reliability is undefined.
- **`by_donors` covers far fewer targets** (4,880 vs 33,983) and 9 fewer genes (10,273 vs 10,282):
  donor-pair DE was only fit where a target passed DE-eligibility within just those two donors' cells.
- The **`h5ad` layers are the aggregate** (both guides, all donors combined) per-gene DE. They give
  the effect magnitude `E_t` (via `log_fc` / `zscore`) but carry **no** guide- or donor-resolution.

### Where the reliability numbers already live (h5ad `.obs`)

The pre-computed reliability scalars are in `DE_stats.h5ad` `.obs` — you do **not** recompute them for
the MVP:

- `guide_correlation_all` — Pearson r between the **two guides'** per-gene DE z-scores, across all
  10,282 genes; `NaN` for single-guide targets. First-pass `R^guide_t`. Also `_signif` (restricted to
  significant genes) and `_pval` variants.
- `donor_correlation_all_mean` / `_min` — mean / min over the disjoint donor-pair Pearson r of per-gene
  DE log-fold-changes; `_hits_*` restrict to per-target hit genes. First-pass `R^donor_t`.

Effect + QC fields also live in `.obs`: `ontarget_effect_size`, `n_total_de_genes`, `n_downstream`
(trans-effects), `ontarget_significant`, `n_guides`, `single_guide_estimate`, `neighboring_gene_KD`,
`distal_offtarget_flag`, `low_target_gex`, `n_cells_target`.

---

## 4. Download-scope decision — do we need all of it?

The scope is driven by the analysis goal, not by "grab everything". Mapping each goal to the minimum
data:

> **Updated by the 2026-07 reframe (issue #8 → change `generalizability-decomposition`).** The deliverable
> is now the full **distribution-light decomposition** (design §10.4), so the two `h5mu` are **core inputs**,
> not MVP-optional. The earlier "`h5ad` alone is sufficient" answer held only for the retired heuristic MVP.

| Analysis goal | Needs | Have it? |
|---|---|---|
| **Headline: distribution-light decomposition** (design §10.4) | `by_guide.h5mu` + `by_donors.h5mu` (**core inputs** — the paired per-guide / per-donor-pair vectors) | ✅ |
| **Corroboration: criterion validation** (design §13) | `K562_comparison.suppl_table.csv` (+ arrayed `Th1Th2` if available) | ✅ K562 fetched · ⚠ `Th1Th2` unavailable |
| **Knockdown-normalized effect** `Q_t` covariate (design §11) | `guide_kd_efficiency.suppl_table.csv` | ✅ fetched |
| **Sanity-check stepping-stone** `E × R × Q` (design §9) | `DE_stats.h5ad` only (`.obs` reliability + `.layers` effect) | ✅ |

**Verdict.** The two 46 GB `h5mu` are **required** — they are the raw per-guide / per-donor-pair vectors the
distribution-light decomposition (§10.4) consumes. The 16.8 GB `h5ad` alone runs only the retired heuristic
(now the labelled sanity-check stepping-stone). So "did we need to download everything?" is now **yes for the
core h5mu** (the h5ad-only path is the stepping-stone, not the deliverable). The criterion inputs
`K562_comparison` and `guide_kd_efficiency` are **now fetched** from the companion repo; the arrayed
`Th1Th2_validation_summary` remains **unavailable** (404 on S3, absent by name in the companion repo), so
criterion validation is **K562-only and marked partial** (design §13).

**Two gaps the download did not cover — and they are the important ones:**

1. **`K562_comparison.suppl_table.csv`** and **`guide_kd_efficiency.suppl_table.csv`** are small,
   **not on S3**, and served from `emdann/GWT_perturbseq_analysis_2025/metadata/suppl_tables/`
   (confirmed present in the repo tree). The K562 table is one half of the §13 criterion; the KD table
   is the §11 covariate. Both should be fetched from the companion repo.

2. ⚠ **`Th1Th2_validation_summary.suppl_table.csv`** — the arrayed bulk-RNA + flow criterion that
   `design.md` §13 (and §2.1) names as *the* external criterion — is **404 on S3** and **absent by that
   exact name in the companion repo tree**. What the companion repo does carry is
   `IL10_IL21_arrayed_validation.csv` + `IL10IL21bulkRNAseq_DESeq2_results.csv` (a *different* arrayed
   validation, IL10/IL21 rather than Th1/Th2), plus the `Th2_Th1_polarization_signature_DE_results_full`
   *signature* table (not a validation summary). **#2 must reconcile the §13 arrayed criterion**: either
   the Th1Th2 summary is served elsewhere (paper supplement), or the arrayed criterion should be built
   on the IL10/IL21 validation that is actually available. This is the single most important thing to
   resolve before the §13 "headline," because K562 alone gives cross-cell-type replication but not the
   arrayed bulk+flow leg.

**Never download:** the 12 cell-level `D*_*.assigned_guide.h5ad` (~1.6 TB). The reliability analysis
works entirely from released summary statistics. `pseudobulk_merged.h5ad` is available on S3 but not
needed (we operate at the DE-stats level, not the pseudobulk level).

---

## 5. Statistical assumptions

Each assumption below states what it is, why it matters, where the design handles it, and how sensitive
the analysis is if it is violated. The design's method choices (ICC over Pearson, permutation null,
hierarchical shrinkage, fixed-condition handling) exist precisely because several of these assumptions
do **not** hold naively.

1. **A crossed measurement design is the right model.** Each perturbation effect is treated as a
   *measured score* whose error decomposes over Target × Guide × Donor × Condition facets + interactions
   + residual (design §4–§5). If the facets are not the operative sources of variation, the whole
   reframing is misplaced. Load-bearing; it is the project's premise.

2. **Reliability-field semantics are consistency on a high-dimensional profile, not scalar
   parallel-forms reliability.** `guide_correlation_all` is a **Pearson r between two ~10k-gene DE
   z-score profiles**, not a reliability coefficient on a single score. Using it as `R^guide_t` as-is
   assumes Pearson consistency ≈ dependability. Design §7–§8 rejects this and upgrades to ICC / Lin's
   CCC (agreement, not mere association); the released Pearson fields are kept only as a first-pass
   proxy and secondary diagnostic.

3. **Agreement, not consistency.** Two guides can correlate `r = 0.9` while one has 3× the magnitude
   (knockdown-efficiency difference). Pearson rewards co-*direction*; reproducibility needs agreement in
   *magnitude*. Violation inflates `R` for guides that merely point the same way. Handled by ICC/CCC
   (design §7).

4. **Effect size and reliability are confounded.** Correlation between two noisy profiles is
   mechanically higher when the true effect is larger (higher SNR), so weak-but-real effects look
   "unreliable" and `E_t × R_dep,t` **double-penalizes** them. Violation biases the ranking against
   moderate genuine effects — the exact population the project wants to rescue. Handled by de-confounding
   `R` from `E` and by the decision-theoretic reformulation (design §9.1, §10.2, §10.3).

5. **The ~10,282 genes in each profile are not independent.** Co-expression and pathway structure make
   the effective degrees of freedom far below the gene count, so the released `_pval` fields are
   anti-conservative. Violation makes "significant" reliability look stronger than it is. Handled by a
   **permutation null** from different-gene guide pairs (design §7).

6. **Condition is a fixed facet; donor and guide are random.** `Rest` / `Stim8hr` / `Stim48hr` are 3
   named biological states, not a sample from a population — so "condition-specificity" is descriptive
   *consistency*, not generalization (design §6, §8.3). Treating condition as random would misattribute
   real T-cell biology to measurement error. Donor (4 levels) and guide (2 levels) are random but tiny,
   so their variance components are noisily estimated.

7. **Sparsity forces partial pooling.** With only 2 guides and 4 donors, per-target variance components
   are under-identified (2 guides = 1 df for `σ²_guide`). The estimable route is a hierarchical /
   partial-pooling REML (or Bayesian) fit with target as a random facet, so `R_dep,t` becomes an
   empirical-Bayes-shrunk posterior quantity carrying its own interval (design §10). This assumes
   **exchangeability of targets** — that targets are draws from a common distribution so strength can be
   borrowed across them. Violation (e.g. distinct target classes) would bias shrinkage.

8. **The object of measurement is the (target × condition) pair.** `n_obs = 33,983` = perturbations ×
   conditions; with condition fixed (assumption 6), reliability is condition-stratified, and a "target"
   is really a target-within-condition. The ranking must decide whether it ranks targets globally or
   per condition (design §8.3 carries two universes).

9. **Single-guide targets have undefined guide reliability.** `guide_correlation_all` is `NaN` for the
   ~7,410 single-guide `(target, condition)` rows (`n_guides = 1`, present in `guide_1` only). The
   analysis must decide how these rank — a QC down-weight and/or fallback to donor reliability, not a
   silent drop or a zero (design §11 treats QC as soft covariates, not hard gates).

---

## 6. Provenance & reproducibility

```bash
# from analysis/data/
bash fetch_data.sh            # 3 CSVs + readme (~14 MB) — always
bash fetch_data.sh --h5ad     # + DE_stats.h5ad (16.8 GB) — the MVP file
bash fetch_data.sh --h5mu     # + by_guide + by_donors h5mu (46 GB) — ICC upgrade / full model
python3 build_codebook.py     # (re)generate CODEBOOK.json from the downloaded files
python3 validate_codebook.py  # verify coverage — exit 0 = pass
```

Companion-repo tables (§13 / §11) are **not** covered by `fetch_data.sh`; fetch them from
`emdann/GWT_perturbseq_analysis_2025/metadata/suppl_tables/` (and resolve the `Th1Th2_validation_summary`
gap, §4) when the analysis reaches criterion validation.

Field-level detail for every column: [`CODEBOOK.json`](./CODEBOOK.json). Method and section pointers:
[`docs/design.md`](../../docs/design.md). Raw data is gitignored (`analysis/data/raw/`); only these
derived docs are tracked.
