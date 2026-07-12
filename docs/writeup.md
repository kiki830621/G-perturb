# G-perturb — research write-up (summary)

> This is a readable summary for browsing in the repository. The **full paper** — methods, the
> derivation of the dependability coefficient, all five figures, the per-condition D-study and
> rank-shift tables, related work, reproducibility, and references — is the LaTeX preprint in
> [`manuscript/`](../manuscript/): [`main.tex`](../manuscript/main.tex) (source) and
> [`main.pdf`](../manuscript/main.pdf) (compiled, 8 pp, bioRxiv format).

Reliability-weighted target prioritization in CD4+ T-cell Perturb-seq, via a generalizability-theory
decomposition.

## Abstract

Genome-wide Perturb-seq screens prioritize candidate targets by the strength of a perturbation's
transcriptional effect. Effect strength does not answer a prior measurement question: is the readout
dependable? A large effect estimated from a single guide, a single donor, or a pseudobulk of few cells
need not survive replication, and for target prioritization each false lead costs a validation
experiment. We treat each perturbation effect as a measurement in a crossed Target × Guide × Donor ×
Condition design and apply generalizability theory (Cronbach et al., 1972) to separate the dependable
part of an effect from facet-specific idiosyncrasy. Guides and donors enter as random facets; condition
enters as a fixed facet and is analyzed within its levels. For each target we report a dependability
profile over the facets and a joint generalizability coefficient over the two random facets, and we
re-rank targets by effect magnitude weighted by that coefficient. On the released screen (Zhu et al.,
2025), removing the measurement-error floor estimated from the non-targeting controls raises the number
of genes with a dependable target-signal share above .10 from 40 to 7,674. A design study indicates that
reliability is limited by the number of guides rather than the number of donors. Analyzed within
activation states, dependability recovers the T-cell-receptor signaling module as reliably measurable
only in activated cells, without recourse to gene annotation. Every methodological decision was recorded
and adversarially reviewed, and all results regenerate from the released summary statistics.

## Findings at a glance

1. *Measurement error masks dependable signal.* Estimating the per-gene noise floor from the
   non-targeting controls and removing it raises the count of genes with a dependable target-signal
   share above .10 from 40 to 7,674 (42% of the genome), with a clean null (non-targeting-vs-non-targeting
   *r* ≈ 0).
2. *A guide-limited design.* A D-study caps the generalizability coefficient near .53 at two guides;
   reaching .70 needs about fifteen guides, and no number of donors suffices — so future screens should
   add guides, not donors. The verdict holds within every activation state.
3. *A reliability-weighted ranking.* Weighting effect size by the per-target dependability drops 49 of
   the top-100 effect-only targets out of the dependability-weighted top-100; reproducible but
   effect-underranked targets rise (RPS3 from rank 79 to 4).
4. *Context-specific dependability recovers real biology.* Sliced by activation state, the T-cell-receptor
   module (CD3D, CD3G, CD247, ZAP70, LAT) is reliably measurable only in activated cells, resting
   dependability at the noise floor — the module reconstructed from dependability alone, without gene
   annotation.

For the full treatment — the crossed design and facet definitions, the dependability profile and joint
coefficient with its derivation, the split-half / Spearman–Brown choice, the recorded cross-model-hardened
process, the figures and tables, and the honest limitations — see
[`manuscript/main.pdf`](../manuscript/main.pdf).
