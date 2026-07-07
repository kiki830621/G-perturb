# G-perturb

**Reliability-weighted target ranking for T cell Perturb-seq via generalizability theory.**

> Built for **Built with Claude: Life Sciences** (Researcher track, 2026), in partnership with Gladstone Institutes. All work in this repository is done from scratch during the hackathon, per the event rules.

---

## The problem

In a Perturb-seq screen, the standard way to rank candidate drug targets is **effect size with FDR control**. That tells you a perturbation moved a lot of genes — but not whether the effect *holds up*. A target with a large effect where its two guides disagree is a worse bet than a moderate effect that stays consistent across guides and donors.

**Reproducibility is the expensive failure mode in target discovery.** G-perturb puts a number on whether a hit will survive when someone else reruns it.

## The insight — it's a measurement problem

The CD4+ T cell Perturb-seq design (Marson & Pritchard labs) maps almost exactly onto a classical psychometric measurement problem:

| Perturb-seq | Psychometric analogue |
|-------------|------------------------|
| Two guides per gene | Two noisy measurements (parallel forms) of one underlying effect |
| Four donors | Four occasions |
| Three stimulation conditions | A crossed facet |

This is the same structure as parallel forms of a test given on different occasions, where you ask how much of the observed score is real signal versus measurement noise.

## The method

1. **Variance decomposition (generalizability theory).** For each perturbation, decompose the effect variance into **guide**, **donor**, and **condition** components (the facets).
2. **Dependability coefficient.** Compute a dependability coefficient (G-theory Φ) for every target — the share of variance that is real, reproducible signal.
3. **Rerank.** Reorder targets by dependability, and surface where this disagrees with the standard differential-expression / effect-size ranking.

## The deliverable

A **reliability-weighted target list**, plus the cases that make the point:

- High effect-size targets that turn out **unreliable** (guides / donors disagree).
- Moderate effect-size targets that turn out **highly dependable**.

Everything reruns on the **released summary statistics** — fully reproducible.

---

## Data

CD4+ T cell Perturb-seq from the Marson and Pritchard labs (a suggested Researcher-track starting point; released with code and preprint). Raw data is **not** committed to this repo — see [`data/`](./data) for how to obtain it.

## Repository layout

```
G-perturb/
├── analysis/   # analysis scripts / notebooks (variance decomposition, dependability, reranking)
├── data/       # instructions to fetch the released statistics (large files gitignored)
├── results/    # reliability-weighted target list and figures
├── LICENSE     # Apache-2.0
└── NOTICE
```

## Reproducing

_To be filled in during the hackathon._

---

## Author

**Che Cheng** — Postdoctoral Research Fellow, Institute of Statistical Science, Academia Sinica

- Website: <https://che-cheng-website.vercel.app>
- ORCID: <https://orcid.org/0000-0003-3376-7833>
- GitHub: <https://github.com/kiki830621>

## License

[Apache License 2.0](./LICENSE) — © 2026 Che Cheng.
