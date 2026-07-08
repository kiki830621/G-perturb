# G-perturb

**A distribution-light generalizability decomposition of CD4+ T cell Perturb-seq — how much of each perturbation's effect is dependable (across guides, donors, conditions) versus irreducible idiosyncrasy, with a reliability-weighted target ranking as a by-product.**

> Built for **Built with Claude: Life Sciences** (Researcher track, 2026), in partnership with Gladstone Institutes. All work in this repository is done from scratch during the hackathon, per the event rules.

> 📄 Full design rationale and method write-up: [`docs/design.md`](./docs/design.md) — the single canonical design. **Headline deliverable (2026-07 reframe, issue #8): the design-level generalizability decomposition** — facet variance shares plus an irreducible replication floor, estimated distribution-light — with the scalar ranking demoted to a sanity-check stepping-stone and criterion validation as corroboration.

---

## The reframing

Target prioritization in Perturb-seq usually ranks by differential-expression strength — effect size, z-score, FDR, number of downstream DE genes. That answers one question:

> Did this perturbation move the transcriptome **in this dataset**?

It does **not** answer the question target discovery actually depends on:

> Will the effect **hold up** with another guide, another donor, another cell-state context?

These are different questions. A target can have a large apparent effect but be fragile (two guides disagree, one donor drives it, weak knockdown, off-target flag). A moderate-effect target that is consistent across guides and donors may be the better validation bet. **G-perturb treats each perturbation effect as a measured score and decomposes its variance across guide, donor, and condition facets — reporting how much of the effect is dependable versus irreducible idiosyncrasy, distribution-light.** The reliability-weighted target ranking (effect magnitude × dependability × quality) falls out as a by-product / sanity-check, not the headline.

## Why it's a measurement problem

The experimental design maps cleanly onto a psychometric measurement design:

| Perturb-seq structure | Measurement-theory analogue |
|---|---|
| Target gene | Object of measurement |
| True perturbation signature | Universe (true) score |
| Two guides per gene | Parallel forms |
| Four donors | Occasions / donor panel |
| Three stimulation conditions | Crossed context facet |
| Cell sampling + sequencing noise | Residual error |

Classical test theory writes `X = T + E`. Generalizability theory decomposes the error into named sources:

```
E = E_guide + E_donor + E_condition + E_interactions + E_residual
```

## The model

A crossed-facet random-effects model over a scalar (or low-dimensional) perturbation score:

```
y[t,g,d,c] = μ + T_t + G_g + D_d + C_c
             + (TG) + (TD) + (TC) + (GD) + (GC) + (DC) + (TGDC)
```

with a per-target empirical dependability score

```
R_dep,t = σ²_signal,t / ( σ²_signal,t + σ²_error,t )
```

`R_dep,t` is a target-specific quantity *inspired by* G-theory. The classical G-theory coefficients — `Eρ²` (relative decisions) and `Φ` (absolute decisions) — are design-level: one per measurement design, not one per target. So the per-target score is named `R_dep,t`, not classical `Φ_t`.

Two honest constraints shape how this is estimated (not optional caveats — they drive the method):

- **Only 2 guides / 4 donors.** Per-target variance components are under-identified (2 guides = 1 df). The estimable "complete" decomposition is a **hierarchical / partial-pooling REML** with target as a random facet, so `σ²_guide`, `σ²_donor`, … are estimated by borrowing strength across targets, and `R_dep,t` is an empirical-Bayes–shrunk quantity. Not per-target ANOVA.
- **Condition is biology, not just error.** Rest / Stim8hr / Stim48hr are real T-cell states. So the project reports **two rankings**: a *global* one (condition treated as a random facet, entering error) and a *context-specific* one (condition treated as a fixed stratifier, one universe per state).

## The score

```
Priority_t = E_t × R_dep,t × Q_t          (× optional Biology_t)
```

- `E_t` — effect magnitude (effect-norm, mean |z|, or number of downstream DE genes)
- `R_dep,t` — empirical dependability (first-pass from released guide/donor correlation fields; full version from the variance components above). Reported as a scalar for ranking (#2), or as a per-domain profile `(R^guide, R^donor, R^condition)` for a diagnostic evidence map (#3).
- `Q_t` — quality penalty: weak on-target knockdown, single-guide estimate, off-target/neighbor flags, low cell support
- `Biology_t` (optional) — pathway / cell-state / disease-genetics relevance, kept explicit so dependability is never mistaken for importance

## Data

Zhu et al. (2025), *Genome-scale perturb-seq in primary human CD4+ T cells* (Marson & Pritchard labs), bioRxiv `2025.12.23.696273`. Genome-scale CRISPRi, ~22M primary human CD4+ T cells, **4 donors × 3 conditions** (`Rest`, `Stim8hr`, `Stim48hr`). Public S3, no credentials:

```
s3://genome-scale-tcell-perturb-seq/marson2025_data/
```

| Stage | Files | Size |
|---|---|---|
| Metadata + QC | `suppl_tables/{DE_stats, sgrna_library_metadata, sample_metadata}.suppl_table.csv` | ~14 MB |
| **Heuristic MVP** (`R_dep,t` from pre-computed correlations) | `GWCD4i.DE_stats.h5ad` (`.obs` guide/donor correlations + `.layers` z-scores) | 16.8 GB |
| **Full variance decomposition** | `GWCD4i.DE_stats.by_guide.h5mu` + `GWCD4i.DE_stats.by_donors.h5mu` | 29 GB + 16 GB |
| Not needed | `D*_*.assigned_guide.h5ad` ×12 (cell-level) | 110–161 GB each (~1.6 TB) — **do not download** |

Note: the flat `DE_stats.suppl_table.csv` is a *reduced* 16-column release — it does **not** carry the reliability correlation fields (`guide_correlation_all`, `donor_correlation_*`). Those live in `GWCD4i.DE_stats.h5ad` `.obs`, so even the heuristic MVP reads the h5ad. The per-facet `.h5mu` files carry the raw guide-/donor-resolved effect vectors needed to fit the crossed variance-component model. Raw data is not committed to this repo (see `analysis/data/CODEBOOK.json` + `fetch_data.sh`).

## Deliverables

- **Reliability-weighted target list** — conventional DE rank vs reliability-weighted rank, with rank shift.
- **High-effect / low-reliability** targets (large DE, guides or donors disagree — fragile).
- **Moderate-effect / high-reliability** targets (better validation bets than a large fragile hit).
- **Context-specific dependable** targets (robust within Rest / Stim8hr / Stim48hr).
- Figures: effect-vs-reliability scatter, rank-shift plot, guide/donor agreement, QC waterfall.
- Reproducible notebook/script from released summary statistics — no 22M-cell processing required.

## Repository layout

```
G-perturb/
├── analysis/
│   ├── data/     # released summary statistics + CODEBOOK.json (large files gitignored)
│   └── ...       # analysis scripts / notebooks
├── docs/         # design rationale (single canonical design.md)
├── results/      # ranked tables and figures
├── LICENSE       # Apache-2.0
└── NOTICE
```

## Author

**Che Cheng** — Postdoctoral Research Fellow, Institute of Statistical Science, Academia Sinica
· <https://che-cheng-website.vercel.app> · ORCID <https://orcid.org/0000-0003-3376-7833> · GitHub <https://github.com/kiki830621>

## License

[Apache License 2.0](./LICENSE) — © 2026 Che Cheng.
