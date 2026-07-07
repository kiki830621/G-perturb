# Domain-Specific Generalizability for Reliability-Weighted Target Ranking in CD4+ T Cell Perturb-seq

## 1. Core Idea

This project reframes **target prioritization in CD4+ T cell Perturb-seq** as a question of **domain-specific generalizability**.

The original target-discovery question is usually:

> Which perturbations produce the largest or most statistically significant transcriptomic effects?

This project asks a different question:

> **For each candidate perturbation effect, where does the evidence generalize, and where does it fail?**

In this framing, a target is not simply "reliable" or "unreliable."  
A target may be reliable across **guides** but not across **donors**; reliable within a **stimulation condition** but not across conditions; or broadly dependable across all observed measurement domains.

The method therefore produces not only a ranked list of candidate targets, but a **generalizability profile** for each target.

---

## 2. Dataset Context

The dataset is the **Primary Human CD4+ T Cell Perturb-seq** resource from the Marson and Pritchard labs.

According to the public dataset page and preprint, the experiment perturbed all expressed genes across approximately **22 million primary human CD4+ T cells**, from **four donors**, under **three stimulation conditions**.

The three major experimental domains are:

| Domain | Dataset analogue | Measurement-theory analogue |
|---|---|---|
| Guide | two sgRNAs targeting the same gene | parallel forms / alternative measurements |
| Donor | four human blood donors | persons / biological contexts to generalize across |
| Condition | Rest, Stim8hr, Stim48hr | experimental contexts / occasions / settings |

The public dataset includes several levels of data:

1. **Cell-level AnnData files**  
   Single-cell expression profiles with guide assignments, donor IDs, condition labels, and QC metadata.

2. **Pseudobulk data**  
   Aggregated expression by guide × donor × condition.

3. **Target-level DE statistics**  
   Differential expression results for each perturbed target × condition.

4. **Guide-level DE statistics**  
   Separate DE profiles for each guide targeting the same gene.

5. **Donor-pair DE statistics**  
   DE profiles estimated from donor subsets, useful for cross-donor consistency checks.

The released summary statistics reportedly include useful reliability/QC fields such as guide correlations, donor correlations, FDR-adjusted p values, log fold changes, z-scores, on-target knockdown measures, single-guide flags, and off-target flags.

---

## 3. Why This Is Not Just a Standard Ranking Problem

A standard Perturb-seq ranking may prioritize targets by:

$$
\text{effect size},\quad z\text{-score},\quad p\text{-value},\quad \text{FDR},\quad \#\text{DE genes}
$$

These statistics answer:

> Did this perturbation move the transcriptome?

They do **not** directly answer:

> Will this perturbation effect hold up if we change the guide, donor, or stimulation context?

That second question is a measurement question.

Target discovery often fails not because the original hit was insignificant, but because the hit was **fragile**:

- it depended on one guide;
- it appeared in only one donor;
- it was driven by one condition;
- it reflected an off-target or low-quality perturbation;
- or it failed to reproduce in follow-up validation.

This project adds a reliability layer to target discovery:

$$
\text{Target priority}
=
\text{effect magnitude}
\times
\text{biological relevance}
\times
\text{domain-specific dependability}
\times
\text{QC}
$$

---

## 4. Generalizability Theory Framing

Generalizability Theory, or G-theory, decomposes observed variation into multiple sources of variation called **facets**. A G study estimates variance components; a D study uses those variance components to evaluate alternative measurement or decision designs.

In the present project:

| G-theory term | Perturb-seq version |
|---|---|
| object of measurement | target gene / perturbation |
| facet | guide, donor, condition |
| observed score | perturbation effect score or transcriptomic effect profile |
| universe of admissible observations | the guide, donor, and condition domains to which we want to generalize |
| G study | variance decomposition of target effects across facets |
| D study | design projection: what happens if we add guides, donors, or change the condition universe? |

The key point is that the **universe of generalization must be defined explicitly**.

A target can be dependable with respect to one universe but not another.

For example:

- dependable across guides;
- dependable across the available donor panel;
- dependable within Stim8hr;
- not dependable across Rest, Stim8hr, and Stim48hr jointly.

---

## 5. The Main Conceptual Shift

The earlier version of this idea used one reliability-weighted target ranking.  
The improved version uses a **domain-specific generalizability profile**.

Instead of asking:

$$
\text{Is target } t \text{ reliable?}
$$

we ask:

$$
\text{Reliable with respect to which domain?}
$$

For each target $t$, estimate:

$$
R_t =
(
R^{guide}_t,\;
R^{donor}_t,\;
R^{condition}_t
)
$$

where:

- $R^{guide}_t$: guide-domain generalizability;
- $R^{donor}_t$: donor-domain generalizability;
- $R^{condition}_t$: condition-domain generalizability.

This profile is more informative than a single scalar score because it diagnoses *why* a target is fragile or dependable.

---

## 6. Domain 1: Guide Generalizability

### Question

> If we use another guide targeting the same gene, do we recover the same perturbation effect?

This is the domain closest to classical measurement reliability.  
Two guides targeting the same gene are analogous to two parallel test forms.

### Suggested metric

Let:

$$
\mathbf{z}_{t,g,c}
$$

be the DE z-score profile for target $t$, guide $g$, condition $c$.

A simple guide-domain reliability score is:

$$
R^{guide}_{t,c}
=
cor(
\mathbf{z}_{t,g=1,c},
\mathbf{z}_{t,g=2,c}
)
$$

A condition-averaged score is:

$$
R^{guide}_{t}
=
mean_c
\left[
R^{guide}_{t,c}
\right]
$$

### Interpretation

| Pattern | Interpretation |
|---|---|
| high guide generalizability | both guides recover similar transcriptomic signatures |
| low guide generalizability | possible guide artifact, guide-efficiency difference, off-target effect, or unstable target effect |
| one-guide-only target | low-confidence target unless supported by strong external evidence |

Guide generalizability should usually be treated as a **measurement-quality issue**, not as biological heterogeneity.

---

## 7. Domain 2: Donor Generalizability

### Question

> Does the perturbation effect generalize across human donors?

In this dataset, donor generalizability is constrained by the fact that there are only four donors. Therefore, this should be described as **donor-panel generalizability**, not population-level human generalizability.

### Suggested metric

Let:

$$
\mathbf{z}_{t,d,c}
$$

be the estimated perturbation effect profile for target $t$, donor or donor subset $d$, condition $c$.

A donor-domain score can be:

$$
R^{donor}_{t,c}
=
mean_{d_i < d_j}
cor(
\mathbf{z}_{t,d_i,c},
\mathbf{z}_{t,d_j,c}
)
$$

or, using donor-pair DE summaries:

$$
R^{donor}_{t,c}
=
mean_{p_i < p_j}
cor(
\mathbf{z}_{t,p_i,c},
\mathbf{z}_{t,p_j,c}
)
$$

where `p_i` and `p_j` are donor-pair subsets.

### Interpretation

| Pattern | Interpretation |
|---|---|
| high donor generalizability | effect is stable across the available donor panel |
| low donor generalizability | effect may be donor-specific, fragile, or driven by one donor |
| donor-specific effect | not necessarily bad; may suggest precision-immunology biology |

Donor variation is not purely error. It may reflect real human biological heterogeneity. Therefore, low donor generalizability should be flagged as:

> "requires more donor validation"

rather than automatically discarded.

---

## 8. Domain 3: Condition Generalizability

### Question

> Does the perturbation effect generalize across T cell stimulation states?

The three conditions are approximately:

- Rest;
- Stim8hr;
- Stim48hr.

Condition generalizability is conceptually different from guide generalizability.  
A condition-specific effect may be biologically meaningful rather than unreliable.

### Two decision universes

#### A. Cross-condition universe

Question:

> Which targets have stable effects across Rest, Stim8hr, and Stim48hr?

This identifies broad or core T cell regulators.

A possible score:

$$
R^{condition}_t
=
mean_{c_i < c_j}
cor(
\mathbf{z}_{t,c_i},
\mathbf{z}_{t,c_j}
)
$$

#### B. Within-condition universe

Question:

> Which targets are dependable within a specific stimulation context?

This identifies condition-specific regulators.

For example:

$$
R^{dep}_{t,Stim8hr}
=
f(
R^{guide}_{t,Stim8hr},
R^{donor}_{t,Stim8hr},
Q_{t,Stim8hr}
)
$$

### Interpretation

| Pattern | Interpretation |
|---|---|
| high cross-condition generalizability | broad/core regulator |
| low cross-condition but high within-condition generalizability | context-specific regulator |
| low within-condition generalizability | fragile evidence even inside one biological state |

The key principle:

> Condition disagreement should not automatically be treated as error. It may be the biological signal.

---

## 9. Target-Level Generalizability Fingerprint

Each target can be assigned a profile:

$$
G_t =
(
E_t,\;
R^{guide}_t,\;
R^{donor}_t,\;
R^{condition}_t,\;
Q_t
)
$$

where:

- $E_t$: effect magnitude;
- $R^{guide}_t$: guide-domain generalizability;
- $R^{donor}_t$: donor-domain generalizability;
- $R^{condition}_t$: condition-domain generalizability;
- $Q_t$: perturbation quality / QC.

Example interpretation table:

| Target type | Guide | Donor | Condition | Interpretation |
|---|---:|---:|---:|---|
| broadly dependable | high | high | high | robust candidate target |
| guide-fragile | low | high | high | likely guide artifact or poor guide design |
| donor-fragile | high | low | high | donor-specific or insufficiently general |
| context-specific | high | high | low | stable within condition but not across states |
| globally fragile | low | low | low | weak candidate for follow-up |

This is the core deliverable: a **domain-specific target evidence map**, not merely a scalar ranking.

---

## 10. Composite Scores

A scalar score can still be useful for ranking, but it should not replace the profile.

### Broad target score

For targets intended to generalize across guide, donor, and condition domains:

$$
S^{broad}_t
=
E_t
\times
R^{guide}_t
\times
R^{donor}_t
\times
R^{condition}_t
\times
Q_t
$$

This prioritizes broadly dependable targets.

### Condition-specific target score

For context-specific regulators:

$$
S^{condition}_{t,c}
=
E_{t,c}
\times
R^{guide}_{t,c}
\times
R^{donor}_{t,c}
\times
Q_{t,c}
$$

This does **not** penalize cross-condition instability, because condition specificity is the target of discovery.

### Recommended reporting

Report both:

1. **Broad dependable target ranking**  
   Targets stable across guides, donors, and conditions.

2. **Condition-specific dependable target ranking**  
   Targets stable across guides and donors within each condition.

3. **Fragility flags**  
   Targets with large effects but poor guide/donor/condition generalizability.

---

## 11. Relationship to Classical G-theory Coefficients

It is important not to overclaim.

### Design-level coefficients

Traditional G-theory coefficients such as:

$$
E\rho^2
$$

and

$$
\Phi
$$

are usually **design-level** quantities. They describe the reliability of the measurement design under a specified universe of generalization.

- $E\rho^2$: generalizability coefficient for relative decisions.
- $\Phi$: dependability coefficient for absolute decisions.

These should be reported for the overall design or for specified decision universes.

### Target-specific scores

For target ranking, this project defines:

$$
R^{dep}_t
$$

or a vector:

$$
(
R^{guide}_t,
R^{donor}_t,
R^{condition}_t
)
$$

These are **target-specific empirical dependability scores**, inspired by G-theory but not identical to the classical design-level $\Phi$.

Recommended language:

> We report design-level G-theory coefficients to characterize the measurement design, and define target-specific empirical dependability profiles to prioritize candidate targets.

This avoids incorrectly claiming that each target naturally has its own classical G-theory $\Phi_t$.

---

## 12. G Study

A G study estimates how much variation in perturbation effects is attributable to targets and to measurement domains.

A possible mixed model is:

$$
y_{t,g,d,c}
=
\mu
+
T_t
+
G_g
+
D_d
+
C_c
+
TG_{tg}
+
TD_{td}
+
TC_{tc}
+
TGD_{tgd}
+
TGC_{tgc}
+
TDC_{tdc}
+
TGDC_{tgdc}
+
\epsilon_{tgdc}
$$

where:

- $T_t$: target effect;
- $G_g$: guide facet;
- $D_d$: donor facet;
- $C_c$: condition facet;
- interactions involving $T$ indicate domain-specific instability.

Important components:

| Component | Meaning |
|---|---|
| $\sigma_T^2$ | stable target-level signal |
| $\sigma^2_{TG}$ | guide-specific target instability |
| $\sigma^2_{TD}$ | donor-specific target instability |
| $\sigma^2_{TC}$ | condition-specific target instability |
| residual | remaining unexplained instability |

The most important components for this project are those involving $T$, because they describe where target evidence fails to generalize.

---

## 13. D Study

A D study uses the G-study variance components to evaluate alternative measurement designs.

Example D-study questions:

1. **More guides**  
   Would using 3–5 guides per target substantially improve guide-domain dependability?

2. **More donors**  
   Would adding donors improve donor-domain generalizability more than adding guides?

3. **Condition-specific analysis**  
   Does dependability improve when the decision universe is restricted to Stim8hr or Stim48hr?

4. **Broad vs context-specific design**  
   Should future screens optimize for cross-condition targets or condition-specific targets?

For example, if guide-related error dominates:

$$
\sigma^2_{TG}
$$

then increasing the number of guides $n_g$ will reduce the guide-related error component roughly as:

$$
\frac{\sigma^2_{TG}}{n_g}
$$

If donor-related target variation dominates:

$$
\sigma^2_{TD}
$$

then increasing guides will not solve the main problem; future validation should add donors.

---

## 14. Minimal Viable Analysis

The minimal version should be feasible from released summary statistics.

### Step 1. Load target-level DE statistics

Use:

- target;
- condition;
- effect size;
- z-score profile;
- adjusted p value;
- number of DE genes;
- on-target knockdown;
- off-target flags;
- single-guide flags.

### Step 2. Load guide-level DE statistics

For each target-condition pair:

$$
R^{guide}_{t,c}
=
cor(
\mathbf{z}_{t,g=1,c},
\mathbf{z}_{t,g=2,c}
)
$$

### Step 3. Load donor-pair DE statistics

For each target-condition pair:

$$
R^{donor}_{t,c}
=
mean\;cor(
\text{donor-pair DE profiles}
)
$$

### Step 4. Estimate condition generalizability

Across Rest, Stim8hr, Stim48hr:

$$
R^{condition}_t
=
mean_{c_i<c_j}
cor(
\mathbf{z}_{t,c_i},
\mathbf{z}_{t,c_j}
)
$$

### Step 5. Define QC penalty

Example:

$$
Q_t =
I(\text{on-target significant})
\times
I(\text{not off-target flagged})
\times
I(\text{not single-guide-only})
\times
q(\text{cell count})
$$

### Step 6. Produce output tables

1. Broad dependable targets.
2. Condition-specific dependable targets.
3. High-effect but guide-fragile targets.
4. High-effect but donor-fragile targets.
5. Context-specific regulators.
6. Targets requiring more donor validation.

---

## 15. Suggested Figures

### Figure 1. Conceptual design diagram

Target × Guide × Donor × Condition → transcriptomic effect profile.

### Figure 2. Standard ranking vs reliability-aware ranking

Scatter plot:

$$
x = \text{standard effect-size rank}
$$

$$
y = \text{domain-specific dependability rank}
$$

Highlight targets whose rank changes substantially.

### Figure 3. Generalizability fingerprint heatmap

Rows: targets.  
Columns:

- effect size;
- guide generalizability;
- donor generalizability;
- condition generalizability;
- QC.

### Figure 4. Four-quadrant target map

$$
x = \text{effect magnitude}
$$

$$
y = R^{dep}_t
$$

Quadrants:

1. high effect / high dependable;
2. high effect / low dependable;
3. moderate effect / high dependable;
4. low effect / low dependable.

### Figure 5. Domain-failure typology

Separate panels:

- guide-fragile;
- donor-fragile;
- context-specific;
- broadly dependable.

### Figure 6. D-study design curves

Plot expected design-level reliability as a function of:

- number of guides;
- number of donors;
- condition universe.

---

## 16. Main Deliverables

### Deliverable 1. Domain-specific target evidence table

For each target:

| target | condition | effect | FDR | guide generalizability | donor generalizability | condition generalizability | QC | classification |
|---|---:|---:|---:|---:|---:|---:|---:|---|

### Deliverable 2. Broad dependable target list

Targets stable across:

- guides;
- donor panel;
- stimulation conditions.

### Deliverable 3. Condition-specific dependable target list

Targets stable across:

- guides;
- donor panel;

within a condition, but not necessarily across conditions.

### Deliverable 4. Fragile high-effect target list

Targets that look strong by standard DE but are weak in at least one generalizability domain.

### Deliverable 5. Experimental-design recommendation

Based on D-study results:

- add guides;
- add donors;
- stratify by condition;
- or prioritize specific validation designs for specific target classes.

---

## 17. Main Claim

A concise version of the claim:

> Standard Perturb-seq target ranking emphasizes the magnitude and significance of perturbation effects. This project adds a measurement-theoretic layer: for each target, it asks whether the evidence generalizes across guides, donors, and stimulation contexts. The output is not only a reliability-weighted target ranking, but a domain-specific generalizability profile that distinguishes broadly dependable targets, context-specific regulators, donor-fragile hits, and guide-fragile artifacts.

---

## 18. What This Project Does Not Claim

This project does **not** claim that G-theory alone discovers biologically important targets.

It does **not** claim that:

- high reliability means high biological importance;
- high reliability means druggability;
- four donors are sufficient for population-level generalizability;
- condition-specific effects are necessarily unreliable;
- CRISPRi knockdown fully predicts pharmacological inhibition.

Instead, it claims:

> G-theory and empirical dependability scoring can evaluate the stability of evidence supporting candidate targets.

In short:

$$
\text{G-theory is not the discovery engine;}
$$

$$
\text{it is the evidence-stability layer.}
$$

---

## 19. Why This Is Worth Doing

This project is worthwhile because target discovery is often limited not by the absence of candidate hits, but by the abundance of fragile hits.

The method directly addresses a practical problem:

> Which hits are worth spending validation resources on?

It improves target prioritization by distinguishing:

1. **large and dependable effects**;
2. **large but fragile effects**;
3. **moderate but dependable effects**;
4. **context-specific effects**;
5. **donor-specific effects requiring validation**;
6. **guide-specific artifacts**.

This is especially useful in primary human-cell Perturb-seq, where donor variation and stimulation context are central to biological interpretation.

---

## 20. Suggested Short Project Title Options

1. **Domain-Specific Generalizability in T Cell Perturb-seq**
2. **Reliability-Aware Target Discovery from CD4+ T Cell Perturb-seq**
3. **From Effect Size to Evidence Stability in Perturb-seq**
4. **Guide, Donor, and Context Generalizability of T Cell Perturbation Effects**
5. **Measurement-Theoretic Target Prioritization for Perturb-seq**

Recommended title:

> **Domain-Specific Generalizability for Reliability-Aware Target Ranking in CD4+ T Cell Perturb-seq**

---

## 21. Pseudocode Sketch

```python
# Inputs:
# target_level_de: target x condition DE profiles
# guide_level_de: target x guide x condition DE profiles
# donor_pair_de: target x donor_pair x condition DE profiles
# qc_table: on-target KD, off-target flags, cell counts, guide availability

for target in targets:
    for condition in conditions:

        # Effect magnitude
        z_target = target_level_de[target, condition].zscore_vector
        E[target, condition] = norm(z_target)

        # Guide generalizability
        if has_two_guides(target, condition):
            z_g1 = guide_level_de[target, "guide_1", condition].zscore_vector
            z_g2 = guide_level_de[target, "guide_2", condition].zscore_vector
            R_guide[target, condition] = corr(z_g1, z_g2)
        else:
            R_guide[target, condition] = missing_or_penalized_value

        # Donor generalizability
        donor_profiles = [
            donor_pair_de[target, pair, condition].zscore_vector
            for pair in donor_pairs
            if available(target, pair, condition)
        ]
        R_donor[target, condition] = mean_pairwise_correlation(donor_profiles)

        # QC
        Q[target, condition] = compute_qc_penalty(qc_table[target, condition])

        # Condition-specific score
        S_condition[target, condition] = (
            E[target, condition]
            * transform(R_guide[target, condition])
            * transform(R_donor[target, condition])
            * Q[target, condition]
        )

    # Condition generalizability
    condition_profiles = [
        target_level_de[target, condition].zscore_vector
        for condition in conditions
        if available(target, condition)
    ]

    R_condition[target] = mean_pairwise_correlation(condition_profiles)

    # Broad score
    S_broad[target] = (
        mean(E[target, condition] for condition in conditions)
        * mean(transform(R_guide[target, condition]) for condition in conditions)
        * mean(transform(R_donor[target, condition]) for condition in conditions)
        * transform(R_condition[target])
        * mean(Q[target, condition] for condition in conditions)
    )

    # Classification
    classification[target] = classify_target(
        effect=mean(E[target, condition] for condition in conditions),
        guide=mean(R_guide[target, condition] for condition in conditions),
        donor=mean(R_donor[target, condition] for condition in conditions),
        condition=R_condition[target],
        qc=mean(Q[target, condition] for condition in conditions)
    )
```

---

## 22. References and Source Notes

- Primary Human CD4+ T Cell Perturb-seq dataset page, CZI Virtual Cell Models.  
  Describes the dataset as genome-scale Perturb-seq in primary human CD4+ T cells, with approximately 22 million cells, four donors, and three stimulation conditions.

- Zhu et al. preprint, *Genome-scale Perturb-seq in primary human CD4+ T cells*.  
  Describes perturbing all expressed genes across 22 million primary human CD4+ T cells from four donors and measuring transcriptome effects in resting and stimulated states.

- Brennan, R. L. Generalizability Theory.  
  Standard G-theory reference for G studies, D studies, variance components, generalizability coefficients, and dependability coefficients.

- Shavelson and Webb, *Generalizability Theory: A Primer*.  
  Classical source for the use of facets, universes of generalization, and decision studies.

- Monteiro et al. 2019, *Generalizability Theory Made Simple(r)*.  
  Accessible explanation of defining facets, conducting G studies, and evaluating design decisions.

---

## 23. One-Sentence Summary

This project turns Perturb-seq target ranking into a domain-specific measurement problem: not merely asking which perturbations have large effects, but diagnosing whether each effect generalizes across guides, donors, and stimulation contexts.
