## ADDED Requirements

### Requirement: Design-level facet variance decomposition

The system SHALL decompose the total dispersion of the released per-target perturbation profiles into facet-attributable shares for guide, donor, condition, and target × interactions, computed from the released summary statistics without re-processing cell-level data. This decomposition SHALL be the headline deliverable.

#### Scenario: Variance shares produced from released summary statistics

- **WHEN** the reference implementation is run on the downloaded `DE_stats.h5ad`, `by_guide.h5mu`, and `by_donors.h5mu`
- **THEN** it SHALL emit a facet variance-shares table naming each facet and its share of the total dispersion

##### Example: variance-shares table shape

- **GIVEN** the four facets guide, donor, condition, and target × interactions
- **WHEN** the decomposition completes
- **THEN** the table SHALL contain one row per facet with a non-negative share, and the facet shares plus the residual SHALL sum to the total dispersion

### Requirement: Irreducible replication floor

The system SHALL report an irreducible replication floor computed as the dispersion among replicate profiles that share an identical facet vector (for instance the two guides of one target, or the two halves of the donor split). This floor SHALL be the only quantity the deliverable labels "distribution-free", and it SHALL be reported with no distributional assumption.

#### Scenario: Floor reported as an assumption-free lower bound

- **WHEN** identical-spec replicate profiles are compared
- **THEN** the system SHALL report a floor quantifying the residual disagreement that no facet model can explain

### Requirement: Distribution-light estimator with a Gaussian baseline comparator

The primary estimator SHALL be a distance-based or permutational decomposition on the gene-expression profiles, using permutation for inference. The system SHALL also fit a Gaussian crossed REML decomposition on a scalar summary and report it alongside as a baseline comparator. The system SHALL NOT present the Gaussian REML fit as the primary result.

#### Scenario: Primary and baseline both reported

- **WHEN** the decomposition is computed
- **THEN** the system SHALL output both the distance-based or permutational shares and the Gaussian REML baseline shares, each labelled distinctly

### Requirement: Per-target shrunk dependability

The system SHALL produce a per-target dependability `R_dep,t` with an uncertainty interval, obtained by moment-based or Fay-Herriot empirical-Bayes shrinkage of the per-target statistic toward the pooled design-level value, using each target's measured sampling variance as the shrinkage weight. The system SHALL NOT estimate per-target dependability from an unpooled per-target fit alone.

#### Scenario: Sparse per-target estimate is shrunk

- **WHEN** a target has a noisy or extreme per-target statistic with high measured sampling variance
- **THEN** its reported `R_dep,t` SHALL be shrunk toward the pooled value more strongly than a target with low measured sampling variance

#### Scenario: Single-guide target retained, not dropped

- **WHEN** a target is present in the `guide_1` modality only, so cross-guide agreement is undefined
- **THEN** the system SHALL retain the target and account for the missing guide agreement through a quality covariate or a donor-based fallback, and SHALL NOT silently drop the target or set its score to zero

### Requirement: Donor facet modeled as split-half generalizability

The system SHALL model donor generalization as split-half agreement over the released disjoint donor-pair splits or the overlapping donor-pair modalities. The system SHALL NOT model the donor facet as a one-way random effect over four individual donors, because the release does not expose independent per-donor profiles.

#### Scenario: Donor generalization from split-half

- **WHEN** donor generalization is estimated
- **THEN** it SHALL be derived from disjoint-split-half agreement or overlap-aware pair modalities, and SHALL NOT be derived from a four-level one-way variance component

### Requirement: Criterion validation degrades honestly

The system SHALL test whether reliability predicts independent replication against the available criterion data. When the arrayed bulk-and-flow criterion table is unavailable, the system SHALL restrict criterion validation to the available cross-cell-type criterion and SHALL mark the result as partial. The system SHALL NOT fabricate the unavailable criterion leg.

#### Scenario: Missing arrayed criterion marked partial

- **WHEN** the arrayed Th1/Th2 validation table is not available
- **THEN** the system SHALL compute criterion validation from the K562 cross-cell-type table alone and SHALL label the result partial

### Requirement: Outputs conform to the demo export contract

The system SHALL emit its outputs — the variance-shares table, the replication floor, the per-target dependability, and any criterion-validation statistic — as committed artifacts that the static demo consumes without a live backend.

#### Scenario: Demo consumes exported artifacts

- **WHEN** the reference implementation finishes
- **THEN** it SHALL write the variance-shares, floor, and per-target dependability outputs in the committed data-and-figure format the demo reads
