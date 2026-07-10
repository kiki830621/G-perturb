## ADDED Requirements

### Requirement: Frozen evidence bundle

The methodology audit SHALL define one versioned evidence bundle before review begins. The bundle SHALL identify every repository file, Git commit, issue comment, dataset metadata source, and external reference supplied to reviewers. Review passes A and B SHALL use the same bundle, and additional evidence requests SHALL be recorded as findings rather than silently changing a pass input.

#### Scenario: Two blind reviews receive identical evidence

- **WHEN** review passes A and B are launched
- **THEN** both pass records contain the same evidence-manifest version and source identifiers
- **THEN** neither pass record contains the other pass output

#### Scenario: Reviewer requests missing evidence

- **WHEN** a reviewer determines that a claim cannot be assessed from the frozen bundle
- **THEN** the reviewer records an additional-evidence finding with an affected claim and blocking severity
- **THEN** the original pass manifest remains unchanged

### Requirement: Three-pass GPT-5.6 Sol audit

The audit SHALL execute three fresh review tasks with model `gpt-5.6-sol` and reasoning effort `max`. Pass A SHALL review architecture and identifiability, Pass B SHALL perform adversarial statistical review, and Pass C SHALL review the reconciled draft and adjudicate integration and handoff. Each pass SHALL record its task identifier, model, reasoning effort, timestamp, exact prompt, evidence-manifest version, and findings.

#### Scenario: Required review records are complete

- **WHEN** the methodology document is evaluated for approval
- **THEN** it contains exactly one valid Pass A, one valid Pass B, and one valid Pass C record
- **THEN** every record contains all required provenance fields

#### Scenario: Requested model is unavailable

- **WHEN** `gpt-5.6-sol` cannot execute a required pass
- **THEN** the audit status is `blocked`
- **THEN** no different model is represented as satisfying that pass

### Requirement: Finding severity and adjudication gate

Every finding SHALL use the fields `ID`, `pass`, `severity`, `evidence`, `affected claim`, `proposed correction`, `disposition`, and `verification`. Severity SHALL be P0, P1, P2, or P3. Disposition SHALL be `resolved`, `blocked`, or `rejected-with-evidence`. The document SHALL NOT receive `approved` status while any P0 or P1 finding lacks a verified disposition.

#### Scenario: Unresolved P1 blocks approval

- **WHEN** at least one P1 finding has no verification or has disposition `blocked`
- **THEN** the document status is `blocked`
- **THEN** the finding states the evidence or action required to remove the block

#### Scenario: Finding is rejected with evidence

- **WHEN** the owner rejects a reviewer finding
- **THEN** the finding disposition is `rejected-with-evidence`
- **THEN** the record cites direct data, simulation, primary literature, or a formal argument supporting rejection

### Requirement: Estimand registry precedes estimator selection

The methodology document SHALL define an estimand registry before selecting the primary profile estimator. Each estimand SHALL state the object, observational unit, target population, decision universe, facet status, aggregation weights, missingness policy, effect direction, uncertainty target, and allowed claim wording. The registry SHALL distinguish condition-specific effects, fixed-domain averages, relative ranking, absolute hit calls, donor-panel consistency, guide-universe generalization, T-cell replication, and cross-cell-type transportability.

#### Scenario: Estimator is traceable to an estimand

- **WHEN** a primary or sensitivity estimator appears in the methodology document
- **THEN** it references exactly one registered estimand or an explicitly defined vector of registered estimands
- **THEN** its output wording does not exceed the registered claim boundary

### Requirement: Claim-to-data identifiability crosswalk

The methodology document SHALL contain a crosswalk for every variance, reliability, floor, ranking, and validation claim. Each row SHALL name the claim, estimand, observation unit, required variation, available evidence, rank or schema gate, assumptions, status, and allowed wording. Status SHALL distinguish `design-specified`, `empirically-passed`, `marginal-only`, and `not-identifiable`.

#### Scenario: Joint component lacks joint observations

- **WHEN** a claimed interaction requires joint guide-by-donor observations and only marginal h5mu products are available
- **THEN** the claim status is `marginal-only` or `not-identifiable`
- **THEN** the document does not describe the claim as a complete crossed variance component

#### Scenario: Data gate has not run

- **WHEN** the document defines a schema or rank gate but the actual pseudobulk object has not been inspected
- **THEN** the status is `design-specified`
- **THEN** the status is not `empirically-passed`

### Requirement: Profile primary and secondary interpretation layers

The document SHALL define profile-level analysis as the primary method and gene-wise plus pathway-level analyses as secondary sensitivity and interpretation layers. Profile estimator selection SHALL compare precision-weighted multivariate linear decomposition, kernel or distance-based permutation, and robust hierarchical functional modeling against identifiability, additivity, gene dependence, sampling uncertainty, exchangeability, compute, and synthetic recovery. CCC and Pearson SHALL remain diagnostic measures unless separate evidence establishes their factorial decomposition interpretation.

Gene-wise analysis SHALL use a target-blind gene universe, effect estimates with covariance, guide nested within target, direct condition contrasts, cross-target or cross-gene pooling, and atlas-wide followed by stage-wise error control. Pathway analysis SHALL pin gene-set versions, use signed all-gene statistics, and separate competitive from self-contained hypotheses. Results derived from the same CD4 dataset SHALL NOT be labelled independent validation.

#### Scenario: Candidate profile methods are compared before selection

- **WHEN** the document selects a primary profile estimator
- **THEN** it includes a comparison table covering every required criterion for all three candidate families
- **THEN** the selected method has a synthetic or formal verification requirement tied to each central claim

#### Scenario: Pathway evidence uses the full analysis universe

- **WHEN** a pathway method is designated as primary or secondary sensitivity evidence
- **THEN** it consumes signed statistics from the pinned target-blind gene universe
- **THEN** a DE-hit-list hypergeometric result is not the sole supporting test

### Requirement: Replication floor requires identical-spec replicates

The document SHALL define an identical-spec replicate as an independent measurement sharing target, guide, donor, condition, and every modeled specification except replicate or lane identity. Guide pairs and donor split halves SHALL NOT satisfy this definition. If identical-spec replicates are unavailable, the document SHALL set replication floor status to `not-identifiable` and SHALL combine the inseparable highest-order interaction with sampling residual.

#### Scenario: Merged pseudobulk has no replicate dimension

- **WHEN** schema and coverage evidence shows one pseudobulk per target-guide-donor-condition specification
- **THEN** the methodology does not report a distribution-free replication floor
- **THEN** the downstream output contract contains a reason code for the combined residual

#### Scenario: Lane-level replicate artifact becomes available

- **WHEN** an artifact provides two or more independent lanes for the same target-guide-donor-condition specification
- **THEN** the document requires a new rank and confounding audit before enabling a replication-floor estimator

### Requirement: Falsification and validation contract

The methodology document SHALL define synthetic scenarios with known facet components, confounding, missing cells, single guides, low counts, knockdown efficiency, heavy tails, and correlated genes. It SHALL predefine numeric acceptance thresholds for bias, interval coverage, type-I error or FDR, false-sign rate, component recovery, and D-study monotonicity. It SHALL also define NTC negative controls, guide cross-fitting, leave-one-donor-out checks, common-support sensitivity, and an external-evidence taxonomy that separates T-cell replication, assay translation, cross-cell-type transportability, and biological relevance.

#### Scenario: Validation source is used for tuning

- **WHEN** an external dataset informs thresholds, weights, or model selection
- **THEN** the same observations are not labelled untouched validation
- **THEN** a nested holdout or separate validation source is required for an independent claim

#### Scenario: K562 evidence is reported

- **WHEN** K562 comparison data are used
- **THEN** the allowed claim is cross-cell-type transportability
- **THEN** the document does not label the result independent T-cell replication

### Requirement: Durable methodology document and downstream handoff

Apply SHALL create `docs/complete-methodology-review-and-upgrade-plan.md` and add a discoverable status-labelled link in `docs/README.md`. The document SHALL contain the sixteen sections defined by the design, the review provenance, finding ledger, estimand registry, identifiability crosswalk, method comparison, validation contract, degradation rules, and a file-by-file crosswalk for the existing `generalizability-decomposition` change. Apply SHALL NOT modify that downstream change.

#### Scenario: Audit is approved

- **WHEN** all required sections and pass records exist and all P0/P1 findings have verified dispositions other than `blocked`
- **THEN** the document status is `approved`
- **THEN** the downstream crosswalk identifies keep, replace, remove, and add actions with verification targets

#### Scenario: Audit remains blocked

- **WHEN** a P0/P1 finding or empirical data gate remains blocked
- **THEN** the complete document is still published with status `blocked`
- **THEN** `docs/README.md` exposes that blocked status
- **THEN** the downstream statistical implementation remains paused

### Requirement: Paper-grade resolution of blocking findings

Under the project's paper-grade methodology standard, a `blocked` audit SHALL trigger a resolution programme rather than complete the project. The methodology document SHALL record every P0 and P1 finding paired with a machine-checkable unblock-condition carrying a pre-registered numeric threshold, and SHALL state that no profile method is declared primary until every such finding is resolved through empirical work — a frozen evidence manifest over the actual joint pseudobulk plus pre-registered synthetic recovery that meets the frozen falsification gates and controls. A quantity not identifiable from the actual observation design SHALL be reported `not-identifiable` and SHALL NOT be fabricated to satisfy a gate.

#### Scenario: Blocked verdict triggers a resolution programme

- **WHEN** the audit status is `blocked` with unresolved P0/P1 findings
- **THEN** the methodology document names a follow-on empirical resolution programme as the required next step
- **THEN** each P0/P1 finding is paired with a pre-registered numeric unblock-condition
- **THEN** the document does not describe `blocked` as a deliverable final state

#### Scenario: No method is declared primary before resolution

- **WHEN** a profile method is proposed as the primary estimator
- **THEN** the document shows that every P0/P1 finding is resolved and every frozen falsification gate is met by pre-registered synthetic recovery
- **THEN** any quantity not identifiable from the actual observation design is reported `not-identifiable`
