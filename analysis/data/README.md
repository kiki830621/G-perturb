# Data — released summary statistics

This directory holds the **derived documentation** for the CD4+ T cell Perturb-seq data
G-perturb analyses. The **raw data itself is not committed** (it lives in gitignored
`raw/`); fetch it with `fetch_data.sh`. Only our own artifacts are tracked:

| Tracked file | What it is |
|---|---|
| `fetch_data.sh` | Downloads the released summary statistics from public S3 into `raw/` |
| `build_codebook.py` | Reads the downloaded CSVs, auto-profiles columns, merges the readme field dictionary → writes `CODEBOOK.json` |
| `validate_codebook.py` | Independent check that `CODEBOOK.json` documents every column + records the reliability-field gap |
| `CODEBOOK.json` | Field-level codebook: every column's dtype, cardinality, description, and G-theory facet role |
| `raw/` | *(gitignored)* the downloaded data + `data_sharing_readme.md` |

## Source

Zhu, Dann, Yan, Reyes Retana, Goto, Guitche, Petersen, Ota, Pritchard, Marson (2025).
*Genome-scale Perturb-seq in primary human CD4+ T cells.* bioRxiv `2025.12.23.696273`
(Marson & Pritchard labs; CZI Virtual Cells). Public S3, no credentials:

```
s3://genome-scale-tcell-perturb-seq/marson2025_data/
```

HTTPS mirror (used by `fetch_data.sh`, no AWS CLI needed):
`https://genome-scale-tcell-perturb-seq.s3.amazonaws.com/marson2025_data/`

## Facet design (why this maps onto G-theory)

| Facet | Levels | Where it lives |
|---|---|---|
| **Target** (object of measurement) | ~12,748 perturbed genes | `target_contrast` (DE_stats) |
| **Guide** (parallel forms) | ~2 sgRNA / gene | `guide_id` (cell `.obs`), `sgRNA` (library), `by_guide.h5mu` modalities |
| **Donor** (occasions) | 4 | `donor_id` |
| **Condition** (crossed context) | 3 — Rest / Stim8hr / Stim48hr | `culture_condition` |

## The reliability-field finding (issue #1)

The flat **`DE_stats.suppl_table.csv`** is a **reduced 16-column** release: it carries effect
magnitude + basic QC (`ontarget_effect_size`, `n_total_de_genes`, `n_downstream`,
`ontarget_significant`, `offtarget_flag`) but **not** the reliability correlations. Those —
`guide_correlation_all`, `donor_correlation_all_mean/min`, `donor_correlation_hits_*`,
`n_guides`, `single_guide_estimate` — live in `GWCD4i.DE_stats.h5ad` `.obs` (15.6 GB).

Consequence: even the heuristic-MVP dependability `R_t` needs the 15.6 GB h5ad (or the
per-facet `by_guide` / `by_donors` h5mu), **not** just the 4.6 MB CSV. The full
variance-component model (issue #2) needs the per-facet h5mu effect vectors regardless.
`CODEBOOK.json` documents these deferred fields from the readme so the modelling issue can
plan against them.

## Rebuild

```bash
bash fetch_data.sh          # download MB-scale CSVs into raw/
python3 build_codebook.py   # (re)generate CODEBOOK.json
python3 validate_codebook.py  # verify coverage — exit 0 = pass
```
