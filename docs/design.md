# Reliability-Weighted Target Ranking for T Cell Perturb-seq

**Track:** Researcher / Build From the Bench  
**Tool context:** Claude Science  
**Core discipline:** Measurement theory × functional genomics × target prioritization  
**Status:** Project idea / analysis proposal

---

## 1. One-Sentence Summary

This project reframes CD4+ T cell Perturb-seq target ranking as a **measurement reliability problem**: instead of ranking perturbations only by differential-expression effect size or FDR, we estimate whether each candidate effect is stable across guides, donors, and stimulation contexts, then use that reliability evidence to prioritize targets for follow-up.

---

## 2. Dataset

The proposed starting point is the **primary human CD4+ T cell Perturb-seq** dataset from the Marson and Pritchard labs.

The dataset is especially suitable because it has a naturally crossed measurement structure:

- approximately **22 million primary human CD4+ T cells**;
- **4 human donors**;
- **3 stimulation conditions**;
- genome-scale CRISPRi perturbation of expressed genes;
- generally **two guides per target gene**;
- released cell-level, pseudobulk, target-level DE, guide-level DE, and donor-level / donor-pair summary outputs.

The important design structure is:

```text
Target gene × Guide × Donor × Stimulation condition → Transcriptomic effect profile
```

This is valuable because the same target is observed through multiple imperfect measurement facets: different guides, different human donors, and different cell-state contexts.

---

## 3. Original Scientific Problem

A standard Perturb-seq target ranking usually emphasizes:

- effect size;
- number of differentially expressed downstream genes;
- z-scores;
- p-values;
- FDR-adjusted significance.

These answer the question:

> Did this perturbation produce a statistically detectable transcriptomic effect?

But target discovery also needs another question:

> Is this effect dependable enough to survive when the experiment is repeated with another guide, another donor, another stimulation context, or another lab?

Those are not the same question.

A target can have a large effect but be unreliable if:

- the two guides disagree;
- the effect is driven by one donor;
- the effect appears in only one condition without clear biological interpretation;
- the on-target knockdown is weak;
- an off-target flag is present;
- the cell count is too low or imbalanced.

Conversely, a target with a moderate effect may be more attractive if its perturbation signature is highly stable across guides and donors.

---

## 4. Key Reframing: This Is a Measurement Problem

The dataset structure maps naturally onto a psychometric measurement framework.

| Perturb-seq component | Measurement-theory analogue |
|---|---|
| Target gene | Object of measurement |
| Two guides for the same gene | Parallel forms / repeated indicators |
| Donors | Occasions / sampled human backgrounds |
| Stimulation conditions | Crossed context facet |
| Transcriptomic effect profile | Observed score / observed response pattern |
| Guide disagreement | Measurement-form error |
| Donor disagreement | Person-background generalization error |
| Condition variation | Context dependence or context-specific biology |

The core idea is not that Generalizability Theory discovers important biological targets by itself. Rather:

> Generalizability Theory evaluates the dependability of evidence for candidate targets.

That distinction is crucial.

---

## 5. What G-Theory Can and Cannot Do

### 5.1 What it can do

Generalizability Theory can decompose observed perturbation-effect variability into multiple sources:

- target-level signal;
- guide-related variability;
- donor-related variability;
- condition-related variability;
- interactions among target, guide, donor, and condition;
- residual error.

It can also support a Decision Study, asking how reliability would change if future screens used:

- more guides per target;
- more donors;
- fewer or more stimulation conditions;
- condition-specific decision universes.

### 5.2 What it cannot do

G-theory cannot, by itself, prove that a target is biologically important, druggable, safe, or clinically relevant.

A reliable perturbation can still be biologically uninteresting. A biologically important target can still have unreliable evidence in this dataset.

Therefore, the final target priority score should combine:

```text
Biological effect magnitude × Biological relevance × Reliability evidence × QC evidence
```

G-theory contributes the **reliability evidence** component, not the entire discovery logic.

---

## 6. G Study vs D Study

### 6.1 G Study: diagnosis of error sources

A **G study** asks:

> In the current dataset, where does measurement variability come from?

For a scalar perturbation score `y`, a simplified crossed model is:

```text
y_tgdc = μ + T_t + G_g + D_d + C_c
          + TG_tg + TD_td + TC_tc
          + TGD_tgd + TGC_tgc + TDC_tdc
          + TGDC_tgdc + e_tgdc
```

where:

- `t` = target;
- `g` = guide;
- `d` = donor;
- `c` = condition;
- `T_t` = target-level signal;
- `TG_tg` = target-specific guide inconsistency;
- `TD_td` = target-specific donor inconsistency;
- `TC_tc` = target-specific condition dependence.

The G study estimates variance components such as:

```text
σ²_T, σ²_TG, σ²_TD, σ²_TC, σ²_TGD, σ²_TGC, σ²_TDC, σ²_residual
```

These components tell us whether unreliability is mainly driven by guide disagreement, donor heterogeneity, condition dependence, or residual noise.

### 6.2 D Study: projected reliability under alternative designs

A **D study** asks:

> If we changed the future measurement design, how would reliability change?

For example, suppose the current screen uses two guides per target. A D study can ask what would happen if future experiments used:

```text
n_g = 2, 3, 4, 5
```

This does not mean the current dataset secretly contains five guides. It means:

> Using G-study variance components, project how much guide-related error would be averaged down if future screens used more guides per target.

For a simplified target × guide design:

```text
Φ(n_g) = σ²_T / (σ²_T + σ²_TG / n_g)
```

If `σ²_TG` is large, increasing the number of guides will improve dependability. If `σ²_TG` is small, more guides will have little benefit.

For the richer target × guide × donor × condition design, the absolute error term can be projected as:

```text
σ²_Δ(n_g, n_d, n_c)
  = σ²_TG  / n_g
  + σ²_TD  / n_d
  + σ²_TC  / n_c
  + σ²_TGD / (n_g n_d)
  + σ²_TGC / (n_g n_c)
  + σ²_TDC / (n_d n_c)
  + σ²_res / (n_g n_d n_c)
```

Then:

```text
Φ(n_g, n_d, n_c)
  = σ²_T / (σ²_T + σ²_Δ(n_g, n_d, n_c))
```

This gives a design-level answer such as:

> Would target dependability improve more by adding guides, adding donors, or separating condition-specific analyses?

---

## 7. G-Coefficient vs Phi Coefficient

G-theory usually distinguishes two design-level coefficients.

### 7.1 G-coefficient

The **G-coefficient** is used for relative decisions.

It asks:

> Can we trust the relative ordering of targets?

It uses **relative error variance**.

A high G-coefficient means that target ranking is stable, even if absolute scores shift across a facet.

### 7.2 Phi coefficient / dependability coefficient

The **Phi coefficient** is used for absolute decisions.

It asks:

> Can we trust the decision that a target is a dependable hit, above a criterion?

It uses **absolute error variance**.

A high Phi coefficient means that hit calls or threshold-based decisions are less sensitive to guide, donor, condition, or other measurement facets.

### 7.3 Why both matter here

In this project:

- **G-coefficient** evaluates whether relative target rankings are stable.
- **Phi** evaluates whether absolute hit decisions are stable.

However, both are traditionally design-level coefficients. They are not automatically one coefficient per target.

---

## 8. Important Correction: Do Not Call the Target-Specific Score Classical Phi

A key methodological point:

> Classical G-theory does not naturally estimate one traditional Phi coefficient for every target.

Classical G-theory usually produces a design-level coefficient:

```text
Φ = σ²_T / (σ²_T + σ²_Δ)
```

This describes the reliability of the measurement design as a whole.

But the proposed target-ranking application needs one reliability-like score per target. Therefore, the proposal should distinguish:

1. **Design-level coefficients**:
   - G-coefficient `Eρ²`;
   - Phi coefficient `Φ`.

2. **Target-specific empirical dependability score**:
   - `R_dep,t`.

The target-specific score is inspired by G-theory, but it should not be presented as a classical textbook Phi coefficient.

Recommended notation:

```text
R_dep,t
```

or:

```text
Φ_emp,t
```

The cleaner option is:

```text
R_dep,t
```

---

## 9. Target-Specific Empirical Dependability Score

For each target `t`, define a reliability-like score using observed consistency evidence.

### 9.1 Guide consistency

Let `z_t,g,c` be the DE z-score profile for target `t`, guide `g`, and condition `c`.

For two guides:

```text
R_guide,t,c = cor(z_t,g1,c, z_t,g2,c)
```

This measures whether two guides targeting the same gene produce similar downstream transcriptomic signatures.

### 9.2 Donor consistency

Using donor-specific or donor-pair DE profiles:

```text
R_donor,t,c = mean pairwise correlation among donor-specific / donor-pair effect profiles
```

This measures whether the perturbation effect is stable across the donor panel.

Because the dataset has only four donors, this should be described as:

```text
donor-panel consistency
```

not:

```text
population-level generalizability
```

### 9.3 Condition stability

There are two possible definitions.

#### Global target reliability

If the desired target should be robust across stimulation contexts:

```text
R_condition,t = consistency across Rest, Stim8hr, Stim48hr
```

#### Context-specific target reliability

If the target may be biologically important only in a specific stimulation state:

```text
R_dep,t,c = dependability within condition c
```

This distinction is important because condition variation may be real biology, not noise.

### 9.4 QC evidence

The score should also include perturbation-quality evidence:

- on-target knockdown effect;
- on-target significance;
- number of guides available;
- single-guide estimate flag;
- off-target flags;
- neighboring-gene knockdown flags;
- low target expression flag;
- cell count / pseudobulk eligibility.

Define:

```text
Q_t = QC penalty or QC weight
```

---

## 10. Proposed Reliability-Weighted Target Score

A simple first version:

```text
Priority_t = Effect_t × R_dep,t × Q_t
```

where:

- `Effect_t` = perturbation effect magnitude, e.g. norm of DE z-score profile, number of DE genes, or biologically selected signature effect;
- `R_dep,t` = empirical dependability score;
- `Q_t` = perturbation-quality score or penalty.

A more complete version:

```text
Priority_t = Effect_t × Biology_t × R_dep,t × Q_t
```

where:

- `Biology_t` = pathway relevance, T cell state relevance, cytokine-program relevance, immune-trait relevance, disease genetics relevance, or expert biological annotation.

This prevents the reliability score from being mistaken for biological importance.

---

## 11. Minimal Viable Analysis

A practical first version can be done entirely from released summary statistics.

### 11.1 Inputs

Use target-level and guide-level / donor-level summaries, such as:

- target-level DE statistics;
- guide-level DE statistics;
- donor-pair DE statistics;
- guide correlation fields;
- donor correlation fields;
- on-target knockdown fields;
- off-target and QC flags.

### 11.2 Steps

1. Load target-level DE summary.
2. Compute effect magnitude per target-condition.
3. Extract or compute guide consistency.
4. Extract or compute donor-panel consistency.
5. Define QC penalty.
6. Construct `R_dep,t`.
7. Construct reliability-weighted priority score.
8. Compare standard DE ranking vs reliability-weighted ranking.
9. Identify disagreement cases.

---

## 12. Key Output Tables

### 12.1 Main ranking table

| target | condition | effect_score | FDR_summary | guide_consistency | donor_consistency | QC_score | R_dep | priority_score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Gene A | Stim8hr | high | low | high | high | pass | high | high |
| Gene B | Rest | very high | low | low | low | warning | low | lower |

### 12.2 Disagreement table

The most important result is not merely the new ranking. It is the disagreement between standard and reliability-weighted ranking.

| category | interpretation |
|---|---|
| high effect / high reliability | strongest candidates |
| high effect / low reliability | fragile hits; likely validation risk |
| moderate effect / high reliability | potentially under-ranked robust targets |
| low effect / low reliability | low priority |

---

## 13. Recommended Figures

### Figure 1. Dataset-as-measurement-design diagram

Show:

```text
Target → measured through guides × donors × conditions → transcriptomic effect profile
```

### Figure 2. Standard ranking vs reliability-weighted ranking

Scatter plot:

```text
x-axis: standard DE/effect ranking
 y-axis: reliability-weighted ranking
```

Highlight targets that move strongly upward or downward.

### Figure 3. Effect size vs dependability

Scatter plot:

```text
x-axis: effect magnitude
 y-axis: R_dep,t
```

Quadrants:

- large and dependable;
- large but fragile;
- moderate but dependable;
- small and fragile.

### Figure 4. D-study design curve

Plot projected design-level `Φ` or `Eρ²` across:

```text
n_guides = 1, 2, 3, 4, 5
```

Optionally repeat for different `n_donor` settings.

### Figure 5. Condition-specific reliability heatmap

Rows = targets.  
Columns = Rest, Stim8hr, Stim48hr.  
Cell value = condition-specific `R_dep,t,c`.

This separates global robust regulators from context-specific regulators.

---

## 14. Why This Is Worth Doing

The project is valuable because it targets a real bottleneck in perturbation-based target discovery:

```text
Significant does not necessarily mean reproducible.
```

Traditional DE / FDR ranking answers:

```text
Did the perturbation move the transcriptome?
```

The proposed reliability layer asks:

```text
Will the observed effect hold up across measurement facets?
```

This is especially important in this dataset because:

- primary human T cells are biologically variable;
- only four donors are available;
- guide-level disagreement can indicate reagent problems or off-target effects;
- condition dependence may represent either unreliability or real context-specific biology;
- follow-up validation is expensive.

Thus, the project should be framed as:

> A reliability-aware target prioritization framework, not a standalone biological discovery engine.

---

## 15. Limitations and Necessary Cautions

### 15.1 Four donors are not enough for population-level generalization

The donor facet can detect obvious donor-panel instability, but it cannot precisely estimate human population heterogeneity.

Use cautious language:

```text
donor-panel consistency
```

not:

```text
generalizability to all humans
```

### 15.2 Condition variation may be biology, not error

Rest, Stim8hr, and Stim48hr may represent distinct biological decision contexts. Therefore, condition should not always be treated as error.

Report both:

- global cross-condition dependability;
- condition-specific dependability.

### 15.3 Reliability is not biological importance

A stable perturbation effect may still be irrelevant to drug discovery. A complete target priority score should include biological relevance and QC.

### 15.4 Classical Phi is design-level

Do not claim that every target has a classical G-theory Phi coefficient unless a target-specific hierarchical model is explicitly defined.

Use:

```text
R_dep,t = target-specific empirical dependability score
```

### 15.5 More guides in D study are projections

D-study guide-number projections assume that additional guides are exchangeable measurements drawn from the same guide design universe.

This is a useful design approximation, not a substitute for actually generating new guides.

---

## 16. Pseudocode

```python
# Pseudocode only

# 1. Load released target-level summary statistics
stats = load_target_level_de_stats()

# 2. Define effect magnitude
stats["effect_score"] = compute_effect_magnitude(
    zscore_profile=stats["zscore_profile"],
    method="l2_norm_or_num_de_genes"
)

# 3. Define guide consistency
stats["R_guide"] = compute_or_extract_guide_correlation(stats)

# 4. Define donor consistency
stats["R_donor"] = compute_or_extract_donor_correlation(stats)

# 5. Define condition-specific or global consistency
stats["R_condition"] = compute_condition_consistency(stats)

# 6. Define QC score
stats["Q"] = compute_qc_weight(
    ontarget_effect=stats["ontarget_effect_size"],
    ontarget_significant=stats["ontarget_significant"],
    off_target_flag=stats["distal_offtarget_flag"],
    single_guide_flag=stats["single_guide_estimate"],
    low_expression_flag=stats["low_target_gex"]
)

# 7. Define empirical dependability score
stats["R_dep"] = combine_reliability_components(
    R_guide=stats["R_guide"],
    R_donor=stats["R_donor"],
    R_condition=stats["R_condition"],
    weights={"guide": 0.4, "donor": 0.4, "condition": 0.2}
)

# 8. Define reliability-weighted priority
stats["priority_score"] = (
    stats["effect_score"]
    * stats["R_dep"]
    * stats["Q"]
)

# 9. Compare standard vs reliability-weighted ranking
stats["standard_rank"] = rank_descending(stats["effect_score"])
stats["reliability_rank"] = rank_descending(stats["priority_score"])
stats["rank_shift"] = stats["standard_rank"] - stats["reliability_rank"]

# 10. Report moved-up and moved-down targets
moved_up = stats.sort_values("rank_shift", ascending=False).head(50)
moved_down = stats.sort_values("rank_shift", ascending=True).head(50)
```

---

## 17. Optional Hierarchical Model Extension

A more formal extension would estimate target-specific reliability using a hierarchical model.

For a scalar effect score:

```text
y_tgdc = θ_t + u_tg + v_td + w_tc + e_tgdc
```

where:

- `θ_t` = latent target effect;
- `u_tg` = guide-specific deviation for target `t`;
- `v_td` = donor-specific deviation for target `t`;
- `w_tc` = condition-specific deviation for target `t`;
- `e_tgdc` = residual.

Then define target-specific empirical reliability from signal-to-error ratio or posterior uncertainty:

```text
R_dep,t = ||E(θ_t | data)||² / (||E(θ_t | data)||² + estimated_error_t)
```

or:

```text
R_dep,t = 1 - posterior_uncertainty_t / prior_or_marginal_uncertainty
```

This is more rigorous but also more model-dependent.

---

## 18. Final Claim

The strongest version of the project claim is:

> This project does not use G-theory to discover biologically important targets by itself. Instead, it uses G-theory and target-specific empirical dependability scores to evaluate whether existing perturbation-effect evidence is stable enough to support target prioritization.

In shorter form:

```text
DE tells us what moved.
Reliability tells us whether we should trust that it moved.
Biology tells us whether the movement matters.
```

The project contribution is the middle layer.

---

## 19. Source Notes

Key factual sources used to frame the proposal:

1. Chan Zuckerberg Initiative / Virtual Cell Models dataset page: **Primary Human CD4+ T Cell Perturb-seq**, describing genome-scale Perturb-seq in primary human CD4+ T cells, approximately 22 million cells, four donors, and three stimulation conditions.
2. BioRxiv preprint: **Genome-scale Perturb-seq in primary human CD4+ T cells**, describing perturbation of all expressed genes across 22 million primary human CD4+ T cells from four donors.
3. Generalizability Theory literature distinguishing G studies, D studies, variance components, G-coefficient for relative decisions, and Phi coefficient for absolute decisions.

