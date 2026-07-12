# Reliability-weighted target prioritization in CD4+ T-cell Perturb-seq: a generalizability-theory decomposition

## Abstract

Genome-wide Perturb-seq screens prioritize candidate targets by the strength of a perturbation's transcriptional effect. Effect strength does not answer a prior measurement question: is the readout dependable? A large effect estimated from a single guide, a single donor, or a pseudobulk of few cells need not survive replication, and for target prioritization each false lead costs a validation experiment. We treat each perturbation effect as a measurement in a crossed Target × Guide × Donor × Condition design and apply generalizability theory (Cronbach et al., 1972) to separate the dependable part of an effect from facet-specific idiosyncrasy. Guides and donors enter as random facets; condition enters as a fixed facet and is analyzed within its levels. For each target we report a dependability profile over the facets and a joint generalizability coefficient over the two random facets, and we re-rank targets by effect magnitude weighted by that coefficient. On the released screen (Zhu et al., 2025), removing the measurement-error floor estimated from the non-targeting controls raises the number of genes with a dependable target-signal share above .10 from 40 to 7,674. A design study indicates that reliability is limited by the number of guides rather than the number of donors. Analyzed within activation states, dependability recovers the T-cell-receptor signaling module as reliably measurable only in activated cells, without recourse to gene annotation. Every methodological decision was recorded and adversarially reviewed, and all results regenerate from the released summary statistics.

## 1. Dependability, not effect size

Target prioritization in Perturb-seq conventionally ranks candidates by differential-expression strength: effect size, *z*-score, false-discovery rate, or the number of downstream differentially expressed genes. These summaries answer whether a perturbation moved the transcriptome *in the observed dataset*. They do not answer whether the effect would hold up under another guide, another donor, or another cell-state context. The two questions come apart. A target can carry a large apparent effect that is fragile, when two guides disagree, one donor drives the signal, knockdown is weak, or an off-target flag is present; a target of moderate effect that is consistent across guides and donors can be the better validation bet. We therefore treat *dependability* as a first-class quantity alongside magnitude.

## 2. A generalizability-theory decomposition

### 2.1 The crossed design and its facets

The experimental structure maps onto a psychometric measurement design. The target gene is the object of measurement; the true perturbation signature is the universe score; the two guides per gene act as parallel forms; the four donors and the three culture conditions are crossed facets; cell sampling and sequencing contribute residual error. Classical test theory writes an observed score as `X = T + E`; generalizability theory decomposes the error term into named sources,

```
E = E_guide + E_donor + E_condition + E_interactions + E_residual,
```

and reports how much of the effect is attributable to each. We distinguish random from fixed facets. Guides and donors are *random* facets: one wants the effect to generalize across the guides and donors that were not sampled. Condition is a *fixed* facet: Rest, Stim8hr, and Stim48hr are three deliberately chosen activation states, not a sample from a population of conditions, so the appropriate treatment is a separate analysis within each state rather than a generalization across states. A perturbation that acts only in the activated state is context-specific, not unreliable, and folding condition into a generalization coefficient would misclassify that signal as noise.

### 2.2 Per-target dependability

For target *t* we summarize dependability as a *profile* of three facet coefficients, reported separately and never multiplied. Each observation is a (target, guide, donor, condition) pseudobulk carrying an effect profile over the 18,129 genes, defined relative to a matched non-targeting-control reference. For a set of observations, the group-mean profile is the elementwise mean, and each facet coefficient is the Pearson correlation, across genes, between two such mean profiles that differ only in that facet:

- `R^guide_t`: the target's guides are split into two halves, each half's mean profile is formed, and the two are correlated. A high value indicates that the transcriptional signature reproduces across independent guide sets.
- `R^donor_t`: the same construction with a two-versus-two donor split, followed by a moment-based empirical-Bayes shrinkage toward the pooled mean, which is warranted because four donors leave the donor coefficient with three degrees of freedom and correspondingly noisy.
- `R^condition_t`: the mean of the pairwise correlations among the three within-state profiles, reported as cross-context *consistency* rather than as a generalization coefficient.

The ranking scalar is the per-target dependability `R_dep,t`, the joint generalizability over the two random facets. Writing each facet coefficient as `R = τ / (τ + e)` for a shared true-score variance `τ` and a facet-specific error variance `e`, the error-to-signal ratios `(1 − R) / R = e / τ` add, so

$$R_{\mathrm{dep},t} = \frac{1}{1 + \dfrac{1 - R^{\mathrm{guide}}_t}{R^{\mathrm{guide}}_t} + \dfrac{1 - R^{\mathrm{donor}}_t}{R^{\mathrm{donor}}_t}}, \qquad S_t = E_t \, R_{\mathrm{dep},t},$$

where `E_t` is the effect magnitude and `S_t` the dependability-weighted score used for ranking. We keep the naming discipline that separates the two levels of the theory: `R_dep,t` is a per-target quantity, whereas the design-level coefficients `Eρ²` and `Φ` describe the measurement design as a whole and carry no per-target subscript.

The joint coefficient has a direct interpretation. Writing an observed profile as `τ_t + ε_guide + ε_donor`, the correlation between two *independent replications* of the whole measurement — a second experiment with fresh guides and fresh donors — is `σ²_τ / (σ²_τ + σ²_guide + σ²_donor)`, which is the expression above. The single-facet coefficients are the same correlation with only one facet refreshed; the joint coefficient refreshes both and is therefore the most stringent form of reproducibility. The equality is exact under the additive model; a guide-by-donor interaction would add a further disagreement term, so the error-adding form is an upper bound when interactions are present.

### 2.3 Split-half versus Spearman–Brown

A split-half correlation estimates the reliability of a *single* level of a facet. The reliability of the deployed design, which averages over the two guides actually used, follows from the Spearman–Brown step-up `R_full = 2r / (1 + r)`. We report the raw single-observation split-half `r`, because the joint coefficient is defined at the single-guide-by-single-donor observation level; the stepped-up value is a separate, larger quantity, appropriate when the question is the dependability of the measurement one actually takes rather than the generalization of a single observation. Both are distribution-light empirical correlations; the Gaussian crossed mixed model is retained only as a baseline comparator, not as the reported estimator.

## 3. Estimation and reproducible adversarial review

The gene-level variance components are estimated with a precision-weighted crossed mixed model fit per gene on the joint pseudobulk. The estimator was not assumed. Three candidates were compared by pre-registered synthetic recovery, and the precision-weighted model was the only one to recover the planted components in both Gaussian and heavy-tailed regimes; a distance-based candidate failed, because a distance share is not a variance component.

The methodology was developed under an auditable process. Each decision — the choice of estimator, the thresholds, the classification of each facet as random or fixed, the criterion for identifiability — was recorded as a versioned issue using issue-driven development (IDD; https://github.com/PsychQuant/issue-driven-development) and spec-driven development, both open-source tooling the author maintains. Because the reasoning was documented rather than implicit, the frozen record could be subjected to adversarial review by an independent frontier model, which returned a blocked verdict with eleven findings, three of them critical, spanning identifiability, measurement error, selection, validation leakage, and compute. Each finding was resolved within the same recorded loop: the falsification gates and controls were frozen before any real result was inspected, the estimator was selected as above, and a mis-specified reliability aggregation (a product of coefficients) was replaced by the joint coefficient of Section 2.2. The resolutions were then cross-verified across models with a second adversarial pass and with parallel-ai-agents (https://github.com/PsychQuant/parallel-ai-agents), a package the author maintains that dispatches a task to independent agents and cross-compares their outputs. The recorded decisions, the blocked verdict, and every resolution are versioned in the repository.

## 4. Results

### 4.1 Measurement error masks dependable signal

The residual of a pseudobulk decomposition combines biological idiosyncrasy with measurement error, and the latter is inflated when a pseudobulk aggregates few cells. The non-targeting controls carry no perturbation, so the variance of the non-targeting effect within its stratum estimates the per-gene measurement-error floor directly. Subtracting this floor from the residual raises the median target-signal share from .019 to .081 and raises the number of genes with a target-signal share above .10 from 40 to 7,674, or 42% of the genome. The dependable signal was present but masked; the same controls give a clean non-targeting-versus-non-targeting negative test (*r* ≈ 0), so the correction introduces no signal where none exists.

### 4.2 A guide-limited design

A design study projects the generalizability coefficient onto alternative numbers of guides and donors. On the representative signal genes the current design (two guides, four donors) reaches `Eρ²` ≈ .44. The guide error term exceeds the donor error term by a factor of about 2.4; adding one guide raises the coefficient about three times as much as adding one donor. With two guides the coefficient is capped near .53, and no number of donors reaches .70, whereas .70 is attainable with about fifteen guides. Guide-to-guide variability, rather than donor heterogeneity, is the binding constraint, which is actionable guidance for the design of subsequent screens. Repeating the design study within each activation state returns the same verdict in all three states, so the recommendation is not an artifact of pooling; within a state the guide term dominates the donor term more sharply still, because most donor disagreement is a cross-state phenomenon.

### 4.3 A reliability-weighted ranking

Ranking targets by `S_t` reorders the candidate list relative to effect size alone. Of the 100 highest-effect targets, 49 fall out of the 100 most dependable, and reproducible targets that effect size underranks rise: RPS3 moves from rank 79 to rank 4, RPP21 from 124 to 8, NMD3 from 158 to 17, IMP4 from 96 to 13, and QARS1 from 53 to 5. These are the targets a dependability-weighted screen would nominate for validation but a strength-ranked screen would overlook.

### 4.4 Context-specific dependability recovers the TCR module

Analyzed within activation states, dependability separates targets that are reliable across all states from targets that are reliable in one state and not another. Because a within-state coefficient rests on roughly a third of the cells and runs lower than the pooled value, states are compared to one another rather than to the pooled number. One hundred targets are context-specific in this sense. Among them, the T-cell-receptor signaling module — the CD3 complex (CD3D, CD3G, CD247) with the proximal kinase ZAP70 and the scaffold LAT — is reliably measurable only in activated cells, with resting dependability at the noise floor (resting `R_dep` ≈ .02–.05; stimulated ≈ .20–.28). The knockdown effect for CD3D grows with activation (effect magnitude .26, .57, and 1.12 across Rest, Stim8hr, and Stim48hr) and becomes dependable only upon activation. The framework reconstructs a coherent signaling module from dependability alone, without gene annotation, which is the strongest available evidence that it measures a real property of the perturbation rather than an artifact of the summary.

## 5. Reproducibility

The pipeline runs end to end from the released summary statistics, without processing the full single-cell data: data retrieval, a checksummed evidence manifest, identifiability gates, synthetic method selection, per-gene decomposition, measurement-error removal, the design study, and the per-context ranking. All results are committed as tables and figures, and every reported number regenerates from a single re-run. The code is released under Apache-2.0.

## 6. Limitations

Four donors leave the donor variance component with three degrees of freedom, so the donor coefficient and the donor axis of the design study carry real uncertainty, which we report as bands rather than point values. Sequencing run is partially confounded with donor, a fact of the released design that we record rather than correct. A small number of full-scale Monte-Carlo gate confirmations are scheduled on a compute cluster; the results shown are the local synthetic and real-data tier. Finally, this is a re-analysis of released data, so the design-study guidance is prospective, addressed to subsequent screens rather than to the present one.

## References

Cronbach, L. J., Gleser, G. C., Nanda, H., & Rajaratnam, N. (1972). *The dependability of behavioral measurements: Theory of generalizability for scores and profiles.* Wiley.

Zhu, R., Dann, E., Yan, J., Reyes Retana, J., Goto, R., Guitche, R. C., Petersen, L. K., Ota, M., Pritchard, J. K., & Marson, A. (2025). Genome-scale perturb-seq in primary human CD4+ T cells maps context-specific regulators of T cell programs and human immune traits. *bioRxiv*. https://doi.org/10.64898/2025.12.23.696273
