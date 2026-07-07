# G-perturb

**Reliability-weighted target ranking for CD4+ T cell Perturb-seq — a generalizability-theory framework for target prioritization.**

> Built for **Built with Claude: Life Sciences** (Researcher track, 2026), in partnership with Gladstone Institutes. All work in this repository is done from scratch during the hackathon, per the event rules.

---

## The reframing

Target prioritization in Perturb-seq usually ranks by differential-expression strength — effect size, z-score, FDR, number of downstream DE genes. That answers one question:

> Did this perturbation move the transcriptome **in this dataset**?

It does **not** answer the question target discovery actually depends on:

> Will the effect **hold up** with another guide, another donor, another cell-state context?

These are different questions. A target can have a large apparent effect but be fragile (two guides disagree, one donor drives it, weak knockdown, off-target flag). A moderate-effect target that is consistent across guides and donors may be the better validation bet. **G-perturb treats each perturbation effect as a measured score and ranks targets by effect magnitude × measurement dependability × perturbation quality.**

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

with a per-target dependability coefficient

```
Φ_t = σ²_signal,t / ( σ²_signal,t + σ²_error,t )
```

Two honest constraints shape how this is estimated (not optional caveats — they drive the method):

- **Only 2 guides / 4 donors.** Per-target variance components are under-identified (2 guides = 1 df). The estimable "complete" decomposition is a **hierarchical / partial-pooling REML** with target as a random facet, so `σ²_guide`, `σ²_donor`, … are estimated by borrowing strength across targets, and `Φ_t` is an empirical-Bayes–shrunk quantity. Not per-target ANOVA.
- **Condition is biology, not just error.** Rest / Stim8hr / Stim48hr are real T-cell states. So the project reports **two rankings**: a *global* one (condition treated as a random facet, entering error) and a *context-specific* one (condition treated as a fixed stratifier, one universe per state).

## The score

```
S_t = E_t × R_t × Q_t
```

- `E_t` — effect magnitude (effect-norm, mean |z|, or number of downstream DE genes)
- `R_t` — dependability (first-pass from released guide/donor correlation fields; full version from the variance components above)
- `Q_t` — quality penalty: weak on-target knockdown, single-guide estimate, off-target/neighbor flags, low cell support

## Data

Zhu et al. (2025), *Genome-scale perturb-seq in primary human CD4+ T cells* (Marson & Pritchard labs), bioRxiv `2025.12.23.696273`. Genome-scale CRISPRi, ~22M primary human CD4+ T cells, **4 donors × 3 conditions** (`Rest`, `Stim8hr`, `Stim48hr`). Public S3, no credentials:

```
s3://genome-scale-tcell-perturb-seq/marson2025_data/
```

| Stage | Files | Size |
|---|---|---|
| Heuristic MVP (first-pass `R_t`) | `suppl_tables/DE_stats.suppl_table.csv` + `sgrna_library_metadata.suppl_table.csv` | 4.6 MB + 9.5 MB |
| **Full variance decomposition** | `GWCD4i.DE_stats.by_guide.h5mu` + `GWCD4i.DE_stats.by_donors.h5mu` | 27 GB + 15.7 GB |
| Not needed | `D*_*.assigned_guide.h5ad` ×12 (cell-level) | 110–161 GB each (~1.6 TB) — **do not download** |

The flat CSV carries pre-computed guide/donor correlations (enough for the heuristic `R_t`); the per-facet `.h5mu` files carry the raw guide-/donor-resolved effect vectors needed to actually fit the crossed variance-component model. Raw data is not committed to this repo.

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
├── results/      # ranked tables and figures
├── LICENSE       # Apache-2.0
└── NOTICE
```

## Author

**Che Cheng** — Postdoctoral Research Fellow, Institute of Statistical Science, Academia Sinica
· <https://che-cheng-website.vercel.app> · ORCID <https://orcid.org/0000-0003-3376-7833> · GitHub <https://github.com/kiki830621>

## License

[Apache License 2.0](./LICENSE) — © 2026 Che Cheng.
