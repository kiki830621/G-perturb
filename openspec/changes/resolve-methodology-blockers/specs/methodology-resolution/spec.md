## ADDED Requirements

### Requirement: Frozen empirical evidence manifest over the joint pseudobulk

The resolution programme SHALL download the joint target-by-guide-by-donor-by-condition pseudobulk and produce a versioned, checksummed evidence manifest before any modeling step runs. The manifest SHALL record, for every target-guide-donor-condition cell, whether it is present, its per-cell library size and cell count, non-targeting-control coverage, and the rank of the associated design matrix. Marginal `by_guide` and `by_donors` products SHALL be treated as comparison or degraded outputs only and SHALL NOT stand in for joint observations.

#### Scenario: Modeling is attempted before the manifest is frozen

- **WHEN** any variance, reliability, floor, or ranking estimator is invoked
- **THEN** a frozen checksummed evidence manifest over the joint pseudobulk exists as its input
- **THEN** no estimator consumes a marginal product in place of a required joint observation

#### Scenario: A joint cell is absent from the design

- **WHEN** the manifest shows a target-guide-donor-condition cell is missing
- **THEN** the missing cell is recorded rather than imputed
- **THEN** any component that requires that cell inherits the missingness in its identifiability status

### Requirement: Empirical identifiability is a fail-closed gate

Every variance, reliability, floor, and ranking claim SHALL pass an empirical design-rank gate and a run/interaction separability gate against the actual design matrix before its estimator runs. When a gate fails, the claim status SHALL be `not_identifiable`, the inseparable highest-order interaction SHALL be combined with sampling residual, and the quantity SHALL NOT be zero-filled or renamed to imply more than the data support. A replication floor SHALL be estimated only when identical-spec replicates exist; otherwise the floor status SHALL be `not_identifiable`.

#### Scenario: Design matrix lacks the rank to separate a component

- **WHEN** the design-rank gate shows a claimed component is not separable at the actual design
- **THEN** the component status is `not_identifiable`
- **THEN** the output contract records a reason code for the combined residual

#### Scenario: No identical-spec replicate exists

- **WHEN** the manifest shows one pseudobulk per target-guide-donor-condition specification
- **THEN** the replication-floor status is `not_identifiable`
- **THEN** no distribution-free replication floor is reported

### Requirement: Measurement-error covariance drives a precision-weighted second stage

The programme SHALL estimate the measurement-error covariance of per-target effects from matched non-targeting controls and SHALL feed it into a precision-weighted generalized-least-squares second stage rather than treating point estimates as error-free. Permutation exchange groups SHALL respect the nested and crossed facet structure. High-dimensional gene dependence SHALL be handled by a low-dimensional basis or shrinkage, and negative variance components SHALL be handled by a boundary-aware estimator rather than truncation that silently changes the estimand. Each inference contract SHALL be calibrated on synthetic data with known ground truth before it is applied to real data.

#### Scenario: Point estimates are used without their measurement error

- **WHEN** a second-stage decomposition consumes per-target effects
- **THEN** it consumes them together with a matched-NTC measurement-error covariance
- **THEN** permutation reshuffling preserves the nested-within-target and donor-crossed structure

### Requirement: Single selective-FDR test tree and separated pathway nulls

Gene-wise analysis SHALL use a target-blind gene universe with one atlas-wide error-control step followed by stage-wise control, and SHALL NOT run an independent uncontrolled FDR per target. Pathway analysis SHALL consume signed all-gene statistics, SHALL separate competitive hypotheses from self-contained hypotheses, and SHALL pin gene-set library versions. A DE-hit-list hypergeometric test SHALL NOT be the sole supporting pathway evidence.

#### Scenario: Pathway claim is evaluated

- **WHEN** a pathway is designated as primary or secondary evidence
- **THEN** it uses a competitive test and a self-contained test reported separately against pinned gene-set versions
- **THEN** the gene universe is the target-blind atlas-wide universe under stage-wise control

### Requirement: Leak-free validation manifest and honest external-evidence taxonomy

The programme SHALL freeze a validation manifest that separates observations used for tuning from observations reserved as holdout, and any observation that informs tuning SHALL NOT be labelled untouched validation. External evidence SHALL be classified by a taxonomy that separates T-cell replication, assay translation, cross-cell-type transportability, and biological relevance, and claim wording SHALL NOT exceed the class.

#### Scenario: A tuning source is later cited as validation

- **WHEN** a dataset informs thresholds, weights, or model selection
- **THEN** the same observations are not labelled untouched validation
- **THEN** an independent claim requires a reserved holdout or a separate source

#### Scenario: K562 evidence is reported

- **WHEN** K562 comparison data are used
- **THEN** the allowed claim is cross-cell-type transportability
- **THEN** the result is not labelled independent T-cell replication

### Requirement: Falsification gates are frozen before any real result

The programme SHALL write a frozen, checksummed gate file enumerating every §7 falsification threshold and §8 control before any real target result is inspected. The gate file SHALL include Monte Carlo scale, type-I error, FDR or false-sign rate, interval coverage, component bias and RMSE, winner's-curse calibration slope, D-study monotonicity, a candidate-disagreement trigger, and compute limits. Any post-freeze change to a threshold SHALL leave an audit trail.

#### Scenario: A real result is inspected before gates are frozen

- **WHEN** a real target ranking or variance component is examined
- **THEN** the frozen checksummed gate file already exists
- **THEN** its thresholds match the review's §7 section

### Requirement: Method selection uses synthetic recovery only

The programme SHALL run pre-registered synthetic recovery for all three candidate profile estimators against the frozen gates and SHALL select the primary method only by synthetic recovery loss. External-validation performance SHALL NOT influence method selection. If no candidate passes every gate, the programme SHALL report that no method qualifies rather than declaring a degraded method primary.

#### Scenario: A candidate looks best on external data but fails synthetic gates

- **WHEN** one candidate has the strongest K562 or arrayed agreement but fails a frozen synthetic gate
- **THEN** it is not selected as the primary method
- **THEN** selection is decided by synthetic recovery loss among gate-passing candidates

#### Scenario: No candidate passes every gate

- **WHEN** all three candidates fail at least one frozen gate
- **THEN** the programme reports that no method qualifies
- **THEN** no candidate is declared primary and the downstream statistical core stays paused

### Requirement: Compute is benchmarked and backed-sparse

The programme SHALL benchmark wall-time and peak memory on a 1 percent and a 10 percent shard before any full-scale run, SHALL keep data backed and sparse without densifying the full gene-by-target matrix, and SHALL size parallel jobs to allocated cores rather than a node's physical cores.

#### Scenario: A full-scale run is launched

- **WHEN** a permutation, bootstrap, or synthetic-recovery run over the full data is launched
- **THEN** a shard benchmark of wall-time and peak memory precedes it
- **THEN** the run does not materialize a dense full gene-by-target matrix
