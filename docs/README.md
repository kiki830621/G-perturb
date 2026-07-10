# docs/ — Design

Single canonical design for G-perturb.

| File | What |
|---|---|
| [`complete-methodology-review-and-upgrade-plan.md`](./complete-methodology-review-and-upgrade-plan.md) | **Status: `blocked`.** The complete dual-layer methodology contract, hardened by a reproducible GPT-5.6 Sol red-team audit (issues #9 / #10). 16 sections + estimand registry + claim→data identifiability crosswalk + profile/gene/pathway model contracts + falsification gates + the `generalizability-decomposition` (#8) file-by-file crosswalk. **`blocked`** = the specified model passes and empirical data gates are not yet complete; #8's statistical core stays paused until this reaches `approved`. |
| [`reviews/`](./reviews/) | Frozen GPT-5.6 Sol review passes (e.g. `sol-pass-b-adversarial-statistical-review.md`, verdict `blocked`). |
| [`design.md`](./design.md) | **The (pre-audit) design.** Reliability-weighted target ranking via generalizability theory: the per-domain generalizability profile `(R^guide, R^donor, R^condition)` as the primary object, the scalar `R_dep,t` ranking as its aggregation, the hierarchical model as the primary method, and criterion validation against the dataset's own arrayed / K562 replication data. Superseded on contested points by the methodology audit above. |

> **Governing status (2026-07).** The methodology audit above is `blocked`. Per the `CLAUDE.md` "Methodology standard — paper-grade, no compromise", `blocked` is **not** a terminal state: the P0/P1 findings must be resolved through a follow-on empirical programme (download the joint pseudobulk, freeze a new evidence manifest, run pre-registered synthetic recovery for all candidates, execute every control, meet every falsification gate) before any profile method is declared primary. Tracked in #10; drives the `audit-complete-methodology` OpenSpec change.

`design.md` is the single source of truth for the pre-audit reframe. It consolidates two earlier drafts — the scalar ranking (issue #2) and the domain-specific profile (issue #3) — into one method, and integrates the methodology critique tracked in issue #4. The scalar ranking and the profile are two **deliverables of one design**, not two designs.

### Naming discipline

- **Target-specific** dependability is `R_dep,t` (scalar) or the profile `(R^guide_t, R^donor_t, R^condition_t)`. It is *inspired by* G-theory, not a classical per-target coefficient.
- **Design-level** G-theory coefficients are `Eρ²` (relative / ranking) and `Φ` (absolute / hit-call) — one per measurement design, reported to characterize the design.
- We never write a per-target `Φ_t`. Classical `Φ` is design-level; the per-target number is `R_dep,t`.
