# Reliability-Weighted Target Ranking for CD4+ T Cell Perturb-seq

**Track:** Researcher / Build From the Bench
**Tool context:** Claude Science
**Discipline:** Measurement theory (generalizability theory) × functional genomics × target prioritization
**Status:** Design / analysis proposal — single canonical source

> This is the **single source of truth** for the G-perturb design. It merges the two earlier drafts — the scalar reliability-weighted ranking (issue #2) and the domain-specific generalizability profile (issue #3) — into one coherent method, and integrates the methodology critique tracked in issue #4. The scalar ranking and the profile are **two deliverables of one design**, not two designs: the profile is the primary object, and the scalar score is an aggregation of it.

---

## 1. One-sentence summary

G-perturb reframes CD4+ T cell Perturb-seq target ranking as a **measurement-reliability problem**: rather than ranking perturbations by differential-expression (DE) effect size or FDR alone, we estimate whether each candidate effect is **dependable** — stable across guides, donors, and stimulation contexts — and use that reliability evidence, together with the dataset's own independent validation data, to prioritize targets for follow-up.

---

## 2. Dataset and its crossed measurement structure

The starting point is the **Primary Human CD4+ T Cell Perturb-seq** resource (Zhu et al. 2025; Marson and Pritchard labs): genome-scale CRISPRi perturbation of expressed genes across ~22 million primary human CD4+ T cells, **4 donors**, **3 stimulation conditions**, generally **2 guides per target gene**.

The dataset is well-suited because the same target is measured through several imperfect facets:

```text
Target gene × Guide × Donor × Condition → genome-wide transcriptomic effect profile
```

### 2.1 Data products actually used (see `analysis/data/CODEBOOK.json`)

| Product | Role |
|---|---|
| `GWCD4i.DE_stats.h5ad` (`.obs` + `.layers`) | **MVP driver.** `.obs` carries pre-computed reliability fields (`guide_correlation_all`, `donor_correlation_all_mean/min`, `donor_correlation_hits_mean/min`, `n_guides`, `single_guide_estimate`, `ontarget_effect_size`, `ontarget_significant`, `distal_offtarget_flag`, `low_target_gex`, …); `.layers` carries the genome-wide `zscore` / `log_fc` / `p_value` / `adj_p_value` vectors per target×condition (`n_obs` = 33,983 target×condition rows) |
| `GWCD4i.DE_stats.by_guide.h5mu` | Guide-resolved effect vectors — needed for the full guide-facet variance component |
| `GWCD4i.DE_stats.by_donors.h5mu` | Donor-resolved effect vectors — needed for the full donor-facet variance component |
| `Th1Th2_validation_summary.suppl_table.csv` | **Independent arrayed validation** (bulk-RNA + flow cytometry) — the external criterion (§13) |
| `K562_comparison.suppl_table.csv` | **Cross-cell-type replication** (`logfc_pearson_r`) — second external criterion (§13) |

Note: the flat `DE_stats.suppl_table.csv` is a *reduced* 16-column release and does **not** carry the reliability correlation fields — even the MVP reads the h5ad.

---

## 3. The scientific problem: significant ≠ reproducible

Standard Perturb-seq ranking emphasizes effect size, number of downstream DE genes, z-scores, p-values, and FDR. These answer:

> Did this perturbation produce a statistically detectable transcriptomic effect?

Target discovery also needs a second question:

> Will this effect hold up when the experiment is repeated with another guide, another donor, another stimulation context, or another lab?

These are not the same question. A target can have a large effect yet be fragile — the two guides disagree, the effect is carried by one donor, the on-target knockdown is weak, an off-target flag is present. Conversely a moderate-effect target can be more attractive if its signature is highly stable. Follow-up validation is expensive, so spending it on fragile hits is the concrete failure this project attacks.

---

## 4. Key reframing: a measurement problem

The dataset structure maps onto a psychometric measurement framework.

| Perturb-seq component | Measurement-theory analogue |
|---|---|
| Target gene | Object of measurement |
| Two guides for the same gene | Parallel forms / repeated indicators |
| Donors | Sampled human backgrounds |
| Stimulation conditions | Crossed context facet |
| Transcriptomic effect profile | Observed response pattern |
| Guide disagreement | Measurement-form error |
| Donor disagreement | Person-background generalization error |
| Condition variation | Context dependence *or* context-specific biology |

The claim is deliberately narrow:

> Generalizability theory does not discover important biology by itself. It evaluates the **dependability of the evidence** for candidate targets.

So the full target-priority logic is a product of independent factors, of which reliability is one:

```text
biological effect magnitude × biological relevance × reliability evidence × QC evidence
```

---

## 5. Generalizability theory: G-study vs D-study

Generalizability theory (G-theory) decomposes observed variation into sources called **facets**. A **G-study** estimates variance components; a **D-study** uses them to project reliability under alternative designs.

### 5.1 G-study — where does error come from?

For a scalar perturbation score `y`, a crossed target × guide × donor × condition model:

$$
y_{tgdc} = \mu + T_t + G_g + D_d + C_c
+ TG_{tg} + TD_{td} + TC_{tc}
+ TGD_{tgd} + TGC_{tgc} + TDC_{tdc}
+ TGDC_{tgdc} + \varepsilon_{tgdc}
$$

with `t` = target, `g` = guide, `d` = donor, `c` = condition. The G-study estimates variance components `σ²_T`, `σ²_TG`, `σ²_TD`, `σ²_TC`, `σ²_TGD`, … , `σ²_residual`. The components involving `T` are the ones that matter here: they say **where target evidence fails to generalize** — guide disagreement (`σ²_TG`), donor heterogeneity (`σ²_TD`), or condition dependence (`σ²_TC`).

### 5.2 D-study — reliability under alternative designs

Using the G-study components, project how error would average down under a future design with `n_g` guides, `n_d` donors, `n_c` conditions:

$$
\sigma^2_\Delta(n_g, n_d, n_c)
= \frac{\sigma^2_{TG}}{n_g}
+ \frac{\sigma^2_{TD}}{n_d}
+ \frac{\sigma^2_{TC}}{n_c}
+ \frac{\sigma^2_{TGD}}{n_g n_d}
+ \frac{\sigma^2_{TGC}}{n_g n_c}
+ \frac{\sigma^2_{TDC}}{n_d n_c}
+ \frac{\sigma^2_{res}}{n_g n_d n_c}
$$

The design-level coefficient is then `σ²_T / (σ²_T + σ²_Δ)`. This answers a design question: would dependability improve more by adding guides, adding donors, or analyzing conditions separately? Because `σ²_TD` is estimated from only 4 donors (3 df), the D-study curves **must carry uncertainty bands** (§6.3, §12) — a projection off a noisy variance component is itself noisy.

---

## 6. Fixed vs random facets — what "generalization" actually means

G-theory only supports *generalization* over facets treated as **random** samples from a universe. Whether a facet is random or fixed changes what a coefficient means, so this must be stated explicitly per facet.

| Facet | Random or fixed | What a high domain score means |
|---|---|---|
| **Guide** | Random (2 guides ≈ sample from a guide-design universe) | Effect generalizes to other guides → genuine target effect, not a reagent artifact |
| **Donor** | Random, but **only 4 donors** | Effect is stable across the *available donor panel* — **not** population-level human generalizability |
| **Condition** | **Fixed** (3 named, biologically meaningful states) | Descriptive **consistency** across 3 specific states — *not* generalization to unobserved conditions |

Consequences:

- Guide and donor D-study projections (§5.2) are legitimate generalization statements (with the 4-donor caveat).
- "Condition generalizability" is a slight misnomer: condition is fixed, so `R^condition` is a descriptive consistency profile axis, and condition-specificity is a discovery target rather than an error to be averaged away (§8.3).

---

## 7. Design-level coefficients vs the target-specific score (naming discipline)

G-theory's classical coefficients are **design-level** — one per measurement design, not one per target:

- `Eρ²` — generalizability coefficient (relative decisions: is the *ranking* of targets stable?);
- `Φ` — dependability coefficient (absolute decisions: is a threshold *hit call* stable?).

Both are reported to characterize the overall design (or a specified decision universe). The per-target ranking application needs one reliability-like number **per target**, which classical G-theory does not naturally provide. So we keep two distinct objects and never conflate them:

- **Design-level:** `Eρ²`, `Φ`.
- **Target-specific empirical dependability:** `R_dep,t` (scalar) or the profile `(R^guide_t, R^donor_t, R^condition_t)`.

`R_dep,t` is *inspired by* G-theory but is **not** a classical per-target `Φ_t`. We never write `Φ_t`.

---

## 8. The per-domain generalizability profile (primary object)

Rather than collapsing to one scalar, each target `t` gets a **profile**:

$$
R_t = \left( R^{guide}_t,\; R^{donor}_t,\; R^{condition}_t \right)
$$

which diagnoses *why* a target is fragile or dependable. Each domain needs a reliability coefficient that measures **agreement, not mere linear association**, and that is **de-confounded from effect size**. Two design decisions apply to all three domains:

- **Use an agreement coefficient, not Pearson r.** Two guides can correlate `r = 0.9` while one has 3× the effect magnitude (differing knockdown efficiency). For reproducibility we want agreement in magnitude, so use an **intraclass correlation (ICC)** or **Lin's concordance correlation coefficient (CCC)**, consistent with G-theory's variance-based dependability. Pearson (consistency) is reported only as a secondary diagnostic. The released `guide_correlation_*` / `donor_correlation_*` fields are Pearson-type and are used as a *first-pass* proxy, upgraded to ICC/CCC in the full analysis.
- **De-confound from effect magnitude.** A raw correlation of two near-zero noise profiles is ~0 regardless of true reliability, so weak-but-real effects look "unreliable" and a naive `E × R` product penalizes effect size twice. Mitigations: restrict the agreement computation to the gene set that is DE in at least one guide; condition on an effect-magnitude stratum; or move to the signal-to-noise / hierarchical formulation (§10) where shrinkage handles low-signal targets naturally.
- **Report a null.** The ~10,000 genes in each profile are not independent (co-expression, pathway structure), so the effective df is far below the gene count and raw sampling variability is understated. Anchor every domain score against a **permutation null** built from agreement between *different-gene* guide pairs.

### 8.1 Guide domain — `R^guide_t`

> If we use another guide for the same gene, do we recover the same signature?

The domain closest to classical measurement reliability (two guides ≈ two parallel forms). Base metric on the DE z-score profile `z_{t,g,c}`, computed as an agreement coefficient (ICC/CCC) between the two guides' profiles, condition-averaged. Low guide generalizability is a **measurement-quality** signal (guide artifact, efficiency difference, off-target), not biological heterogeneity.

### 8.2 Donor domain — `R^donor_t`

> Does the effect generalize across donors?

Agreement across donor / donor-pair effect profiles (`donor_correlation_*` fields as first pass; ICC across donor-resolved vectors from `by_donors.h5mu` in the full version). With only 4 donors this is **donor-panel consistency**, never population-level generalizability. Donor variation is **not pure error** — it can be real precision-immunology biology, so low `R^donor` is flagged as "needs more donor validation" rather than discarded.

### 8.3 Condition domain — `R^condition_t` (fixed facet, two universes)

Because condition is fixed (§6), there are two distinct questions, and we report both:

- **Cross-condition (broad regulators):** agreement of `z_{t,c}` across the 3 states — identifies core regulators.
- **Within-condition (context-specific regulators):** dependability *inside* a state, `R^dep_{t,c} = f(R^guide_{t,c}, R^donor_{t,c}, Q_{t,c})` — identifies context-specific regulators.

Key principle: **condition disagreement may be the biological signal, not noise.** A context-specific regulator is a discovery, not a failure.

---

## 9. The scalar score and ranking (deliverable for #2)

For ranking, aggregate the profile into a scalar. The simplest form:

```text
Priority_t = E_t × R_dep,t × Q_t          (× optional Biology_t)
```

- `E_t` — effect magnitude (z-norm, mean |z|, or number of downstream DE genes; normalized by knockdown efficiency, §10.3);
- `R_dep,t` — empirical dependability, either the scalar aggregate of the profile or a per-domain product;
- `Q_t` — perturbation-quality weight;
- `Biology_t` (optional) — pathway / cell-state / disease-genetics relevance, kept explicit so dependability is never mistaken for importance.

Two composite variants:

$$
S^{broad}_t = E_t \times R^{guide}_t \times R^{donor}_t \times R^{condition}_t \times Q_t
$$

$$
S^{condition}_{t,c} = E_{t,c} \times R^{guide}_{t,c} \times R^{donor}_{t,c} \times Q_{t,c}
$$

`S^broad` prioritizes broadly dependable targets; `S^condition` deliberately does **not** penalize cross-condition instability, because context specificity is the discovery goal. The scalar is a convenience for ordering; it does **not** replace the profile (§8).

### 9.1 Why the multiplicative form is a heuristic, not the objective

The product `E × R × Q` imposes a strong, unmotivated trade-off (any zero factor zeroes the target) and the weights (`guide 0.4, donor 0.4, condition 0.2` in the first-pass code) are arbitrary. The principled target is a **decision-theoretic** quantity (§10.2): the posterior probability that the target's universe-score effect exceeds a decision threshold, `P(τ_t > c | data)`. The multiplicative score is retained only as an interpretable first-pass ranking; the reported ranking should converge to the decision-theoretic one.

---

## 10. Hierarchical model — the primary method (not "optional")

The correlation heuristic is a shadow of the proper model. The hierarchical / empirical-Bayes fit is what (a) yields a per-target reliability **with uncertainty**, (b) dissolves the 2-guide/4-donor sparsity by borrowing strength across targets, and (c) removes the effect-size confound via shrinkage of low-signal targets. It is the primary deliverable; the released correlation fields are the quick-look sanity check, not the reverse.

### 10.1 Model and reliability definition

For a target effect (per gene, or a well-chosen scalar summary):

$$
y_{tgdc} = \theta_t + u_{tg} + v_{td} + w_{tc} + e_{tgdc}
$$

with `θ_t` the latent target effect and `u_tg` / `v_td` / `w_tc` the guide / donor / condition deviations for target `t`. Fit by partial-pooling REML or a Bayesian hierarchical model. Define target-specific reliability as a posterior quantity, which carries its own credible interval:

$$
R_{dep,t} = \frac{\lVert \mathbb{E}[\theta_t \mid \text{data}] \rVert^2}{\lVert \mathbb{E}[\theta_t \mid \text{data}] \rVert^2 + \widehat{\text{err}}_t}
$$

### 10.2 Decision-theoretic ranking

From the same posterior, rank by `P(τ_t > c | data)` where `τ_t` is the universe (fully-generalized) target effect and `c` a decision threshold. This is the absolute-decision (`Φ`) idea turned into an actual per-target decision rule, and it replaces the ad-hoc product of §9.

### 10.3 Coherence gap to close, and KD normalization

The reliability metric uses the genome-wide **vector** (profile agreement) while the variance-component model above is written for a **scalar** `y`. Reconcile by either (a) decomposing per-gene then aggregating, (b) using a profile-level (multivariate / distance-based) generalizability formulation, or (c) defining an explicit scalar summary (e.g. projection onto the target's own leading effect direction). Separately, because a weak effect may reflect poor knockdown rather than no downstream role, `E_t` is normalized to **effect per unit on-target knockdown**, and QC enters the model as a **covariate**, not as a hard multiplicative gate (§11).

---

## 11. QC as a soft, model-level adjustment

Available QC evidence: on-target knockdown effect and significance, `n_guides`, single-guide-estimate flag, distal off-target flag, neighboring-gene knockdown flag, low target-expression flag, cell count / pseudobulk eligibility.

A hard product of indicator functions (`Q = I(sig) × I(¬off-target) × …`) is brittle: one noisy flag zeroes a target. Instead treat QC as **covariates / soft weights** in the model (adjust the effect estimate for knockdown efficiency, down-weight low cell support) and report the flags alongside the ranking rather than multiplying them in. Hard filtering discards information that the model can use.

---

## 12. G-study / D-study outputs

- **G-study:** variance components `σ²_T`, `σ²_TG`, `σ²_TD`, `σ²_TC`, … with standard errors. The `T`-interaction components localize the dominant error source.
- **D-study:** projected design-level `Eρ²` / `Φ` across `n_guides = 1..5` and `n_donor` settings, **with confidence bands** (the `σ²_TD` estimate from 4 donors is unstable). Deliverable: a design recommendation — add guides vs add donors vs stratify by condition — per target class.

---

## 13. Criterion validation — does reliability predict independent replication?

This is the highest-value addition and the data is already in hand. The framework claims `R_dep` predicts follow-up success; the dataset lets us **test that claim in-sample** against independent measurements:

- `Th1Th2_validation_summary.suppl_table.csv` pairs, in one table, the perturb-seq reliability metrics (`pseq_crossguide_corr_signif`, `pseq_crossdonor_corr_hits_mean`) with **independent arrayed outcomes** (bulk-RNA z-scores `bulkRNA_*`, flow-cytometry `flow_*_log2FC`).
- `K562_comparison.suppl_table.csv` gives **cross-cell-type** replication (`logfc_pearson_r`).

Analysis: stratify targets by `R_dep` (and by each domain score) and test whether high-reliability targets replicate better in the arrayed / bulk / flow / K562 data — a reliability→replication curve or AUC. This converts the project from "a proposed score" into "a score shown to predict independent replication," which is the credibility centerpiece. It also lets us **calibrate** the domain weights and the decision threshold `c` against real replication outcomes instead of choosing them arbitrarily.

---

## 14. Target typology (fingerprint)

Assign each target `G_t = (E_t, R^guide_t, R^donor_t, R^condition_t, Q_t)` and classify:

| Target type | Guide | Donor | Condition | Interpretation |
|---|---:|---:|---:|---|
| Broadly dependable | high | high | high | robust candidate |
| Guide-fragile | low | high | high | likely guide artifact / poor guide design |
| Donor-fragile | high | low | high | donor-specific; needs more donor validation |
| Context-specific | high | high | low | stable within a state, not across — a discovery, not a failure |
| Globally fragile | low | low | low | weak follow-up candidate |

This **domain-specific evidence map** is the core deliverable; the scalar ranking is its summary.

---

## 15. Deliverables

1. **Domain-specific target evidence table** — per target × condition: effect, FDR, `R^guide`, `R^donor`, `R^condition`, QC, classification, and `R_dep` with its uncertainty.
2. **Broad dependable ranking** (#2) — targets stable across guides, donor panel, and conditions.
3. **Condition-specific dependable ranking** — targets stable within a state.
4. **Fragile high-effect list** — strong by standard DE but weak in ≥1 domain (the validation-risk list).
5. **Criterion-validation result** (§13) — reliability→replication curve against arrayed / K562 data.
6. **Design recommendation** (D-study) — add guides vs donors vs stratify, per target class.

---

## 16. Minimal viable analysis and staging

| Stage | Inputs | Notes |
|---|---|---|
| **MVP** | `DE_stats.h5ad` (`.obs` correlations + `.layers` z-vectors) | First-pass `R_dep,t` from released Pearson-type correlation fields + QC flags; ranking vs standard DE; disagreement table |
| **Criterion check** | `Th1Th2_validation`, `K562_comparison` CSVs | §13 — cheap join + correlation/AUC; run early, it is the headline result |
| **Full** | `by_guide.h5mu`, `by_donors.h5mu` | Hierarchical variance-component fit (§10); ICC/CCC upgrade; D-study with bands |

Raw data is not committed (rights + size); see `analysis/data/CODEBOOK.json` and `fetch_data.sh`.

Pseudocode (MVP, first pass):

```python
stats = load_de_stats_h5ad()                       # .obs + .layers

stats["effect"]     = effect_magnitude(stats)       # z-norm or #DE genes, KD-normalized
stats["R_guide"]    = guide_agreement(stats)        # released corr → ICC/CCC in full version
stats["R_donor"]    = donor_agreement(stats)        # donor-panel consistency
stats["R_condition"]= condition_consistency(stats)  # fixed facet: cross- and within-condition
stats["Q"]          = qc_weight(stats)              # soft weight, not hard gate

stats["R_dep"]      = aggregate_profile(stats)      # or per-domain product
stats["priority"]   = stats.effect * stats.R_dep * stats.Q

# disagreement is the point, not just the new order
stats["rank_shift"] = rank(stats.effect) - rank(stats.priority)

# criterion validation (the headline)
val = join(stats, load_arrayed_validation())        # Th1/Th2 bulk + flow, K562
reliability_predicts_replication = auc(val.R_dep, val.replicated)
```

---

## 17. Figures

1. **Design diagram** — target measured through guides × donors × conditions → effect profile.
2. **Standard vs reliability-weighted ranking** — scatter; highlight large rank shifts.
3. **Effect vs dependability** — scatter with quadrants (large/dependable, large/fragile, moderate/dependable, small/fragile).
4. **Generalizability fingerprint heatmap** — targets × {effect, `R^guide`, `R^donor`, `R^condition`, QC}.
5. **Domain-failure typology** — panels for guide-fragile / donor-fragile / context-specific / broadly dependable.
6. **D-study design curves** — projected `Φ` / `Eρ²` vs `n_guides`, `n_donors`, with confidence bands.
7. **Criterion-validation curve** — reliability stratum vs independent replication rate (§13).

---

## 18. Limitations and cautions

- **Four donors** detect obvious donor-panel instability but cannot estimate human population heterogeneity — say "donor-panel consistency," not "generalizability to all humans."
- **Condition is biology, not just error** — report both cross-condition and within-condition dependability.
- **Reliability is not importance** — a stable effect can be biologically uninteresting; keep `Biology_t` explicit.
- **Classical `Φ` is design-level** — never claim a per-target `Φ_t`; use `R_dep,t`.
- **D-study projections assume exchangeable future guides/donors** — a design approximation, not a substitute for generating them; carry uncertainty bands.
- **Selection / winner's curse** — ranking ~12k targets by a product of noisy quantities inflates the top; empirical-Bayes shrinkage mitigates but should be stated.
- **Released correlations are pre-computed Pearson** — the genuinely new computation is the variance-component fit and the criterion validation; lead with those.

---

## 19. What this project does not claim

It does **not** claim G-theory alone discovers important biology, that high reliability implies importance or druggability, that 4 donors give population generalizability, that condition-specific effects are unreliable, or that CRISPRi knockdown fully predicts pharmacological inhibition. It claims only:

> G-theory and target-specific empirical dependability evaluate the **stability of the evidence** for candidate targets — and, here, that this stability predicts independent replication.

In short:

```text
DE tells us what moved.
Reliability tells us whether we should trust that it moved.
Validation tells us whether that trust is earned.
Biology tells us whether the movement matters.
```

The project contribution is the middle two layers.

---

## 20. Source notes

1. **Primary Human CD4+ T Cell Perturb-seq** — CZI Virtual Cell Models dataset page (~22M primary human CD4+ T cells, 4 donors, 3 stimulation conditions).
2. **Zhu et al. 2025**, *Genome-scale Perturb-seq in primary human CD4+ T cells* (Marson & Pritchard labs) — perturbs all expressed genes; releases target-/guide-/donor-resolved DE plus reliability/QC fields and independent arrayed + K562 validation tables.
3. **Brennan, R. L.**, *Generalizability Theory*; **Shavelson & Webb**, *Generalizability Theory: A Primer*; **Monteiro et al. 2019**, *Generalizability Theory Made Simple(r)* — G-/D-studies, variance components, `Eρ²` (relative) vs `Φ` (absolute), fixed vs random facets.
4. Reliability-coefficient choice: **ICC** (agreement) and **Lin's concordance correlation** vs Pearson (consistency).
