# G-perturb

**Rank CD4+ T-cell Perturb-seq drug targets by whether the readout is *dependable*, not by how large it is.** G-perturb decomposes each perturbation's effect across guides, donors, and activation states with generalizability theory, then re-ranks targets by how reproducibly their signal generalizes.

> Built for **Built with Claude: Life Sciences** (Researcher track, 2026), in partnership with Gladstone Institutes. All work in this repository is done from scratch during the hackathon, per the event rules.

> 🧬 **Preprint:** posted on bioRxiv on 2026-07-15, DOI [`10.64898/2026.07.13.738312`](https://doi.org/10.64898/2026.07.13.738312) ([read on bioRxiv](https://www.biorxiv.org/content/10.64898/2026.07.13.738312v1)). Manuscript licensed CC BY-NC 4.0; code Apache-2.0.

> **Start here:** [▶ 3-minute demo video](https://youtu.be/zBD30nhal64) · [short summary](./SUMMARY.md) · [full paper (PDF)](./manuscript/main.pdf) · [demo slides](./demo/slides.html) + [voiceover](./demo/read-aloud.md).

> 📄 Full design rationale: [`docs/design.md`](./docs/design.md) (canonical design). 📝 Research write-up (methods + results, paper voice): [`docs/writeup.md`](./docs/writeup.md) — the bioRxiv-format LaTeX preprint is in [`manuscript/`](./manuscript/) ([`main.pdf`](./manuscript/main.pdf)). The **method** is a distribution-light generalizability decomposition — facet variance shares plus an irreducible replication floor. The **deliverables** are a reliability-weighted target ranking and the dependability findings below, all resting on that decomposition.

---

## What we found

On the real 44.6 GB joint pseudobulk (18,129 genes × 4 donors × 3 conditions), decomposed genome-wide:

- **Signal was hidden under measurement noise.** Raw pseudobulk shows dependable target-signal in only **40** genes; removing the measurement-error floor (estimated from the non-targeting controls) lifts that to **7,674 genes (42%)** — the dependable hits were masked by noise, not absent.
- **The ranking reshuffles.** Weighting effect size by a per-target dependability coefficient reorders the shortlist: the effect-only and dependability-weighted rankings correlate at Spearman ρ = 0.74 overall, yet **50 of the top-100 effect-only targets drop out** of the dependability-weighted top-100. Targets you would *miss by effect size alone* climb sharply — **RPS3 #79→#4, QARS1 #53→#5, RPP21 #124→#6, IMP4 #96→#12, NMD3 #158→#14** are dependable but effect-underranked: the "validate these next" candidates.
- **Reliability is guide-limited.** A D-study shows two guides per gene cap generalizability near 0.53; reaching 0.70 needs ~15 guides, and no number of donors suffices — **add guides, not donors** (and this holds within every activation state, not just pooled).
- **Context-specificity recovers real biology, unprompted.** Slicing dependability by activation state surfaces the **T-cell-receptor signaling module — CD3D, CD3G, CD247, ZAP70, LAT — as reliably measurable only in *activated* T cells** (resting dependability at the noise floor). With no gene labels, the method reconstructs the TCR module: the sharpest evidence it measures something real.

Figures (submission-grade): [`analysis/resolution/realdata/figures/`](./analysis/resolution/realdata/figures/). Ranked tables: [`analysis/resolution/realdata/target_ranking.csv`](./analysis/resolution/realdata/target_ranking.csv) + `target_context_specificity.csv`. The whole pipeline regenerates every number from one re-run.

## How it was built — an auditable, cross-model-hardened process

Every scientific decision (estimator, thresholds, why a facet is random vs fixed, what counts as identifiable) was filed as a GitHub issue through **issue-driven development (IDD)** and spec-driven development (Spectra) — open-source Claude Code plugins I built ([`PsychQuant/issue-driven-development`](https://github.com/PsychQuant/issue-driven-development)). That auditable decision ledger let a *competing* frontier model, **GPT-5.6 Sol**, red-team the design: it returned **BLOCKED** with 11 methodological holes (3 critical), and each was worked through in the same loop with Claude — gates frozen before results, the method chosen by pre-registered synthetic recovery. The resolutions were then **cross-verified across models**: a second adversarial pass via **codex-pro** (Codex) and multi-agent cross-checking through [`PsychQuant/parallel-ai-agents`](https://github.com/PsychQuant/parallel-ai-agents) — another package I wrote that dispatches a task to independent Claude and Codex agents and cross-compares their outputs. The blocked verdict and every resolution are versioned in the repo (`docs/reviews/`, `openspec/changes/`, the issue history) — the audit trail *is* the evidence.

*(IDD and Spectra are my pre-existing open-source tooling; the G-perturb analysis they govern here is the new hackathon work.)*

## The reframing

Target prioritization in Perturb-seq usually ranks by differential-expression strength — effect size, z-score, FDR, number of downstream DE genes. That answers one question:

> Did this perturbation move the transcriptome **in this dataset**?

It does **not** answer the question target discovery actually depends on:

> Will the effect **hold up** with another guide, another donor, another cell-state context?

These are different questions. A target can have a large apparent effect but be fragile (two guides disagree, one donor drives it, weak knockdown, off-target flag). A moderate-effect target that is consistent across guides and donors may be the better validation bet. **G-perturb treats each perturbation effect as a measured score and decomposes its variance across guide, donor, and condition facets — reporting how much of the effect is dependable versus irreducible idiosyncrasy, distribution-light.** The reliability-weighted target ranking (effect magnitude × dependability) is the primary deliverable; the variance decomposition is the engine underneath it.

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

Zhu et al. (2025), *Genome-scale perturb-seq in primary human CD4+ T cells maps context-specific regulators of T cell programs and human immune traits* (Marson & Pritchard labs), bioRxiv [doi:10.64898/2025.12.23.696273](https://doi.org/10.64898/2025.12.23.696273). Genome-scale CRISPRi, ~22M primary human CD4+ T cells, **4 donors × 3 conditions** (`Rest`, `Stim8hr`, `Stim48hr`). Public S3, no credentials:

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
├── manuscript/   # bioRxiv-format LaTeX preprint (main.tex, main.pdf, figures)
├── SUMMARY.md    # short written summary
├── demo/         # 1920×1080 slide deck (slides.html) + read-aloud voiceover
├── analysis/
│   ├── data/         # released summary statistics + CODEBOOK.json (large files gitignored)
│   └── resolution/   # the pipeline: gates, controls, synthetic recovery, real-data decomposition, ranking
├── docs/         # design rationale, research write-up, the Sol adversarial review
├── openspec/     # spec-driven-development change records (audit trail)
├── archive/      # exploratory work not used in the final pipeline
├── LICENSE       # Apache-2.0
└── NOTICE
```

## Author

**Che Cheng** — Postdoctoral Research Fellow, Institute of Statistical Science, Academia Sinica
· <https://che-cheng-website.vercel.app> · ORCID <https://orcid.org/0000-0003-3376-7833> · GitHub <https://github.com/kiki830621>

## License

[Apache License 2.0](./LICENSE) — © 2026 Che Cheng.
