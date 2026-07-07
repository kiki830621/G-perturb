# docs/ — Design

Single canonical design for G-perturb.

| File | What |
|---|---|
| [`design.md`](./design.md) | **The design.** Reliability-weighted target ranking via generalizability theory: the per-domain generalizability profile `(R^guide, R^donor, R^condition)` as the primary object, the scalar `R_dep,t` ranking as its aggregation, the hierarchical model as the primary method, and criterion validation against the dataset's own arrayed / K562 replication data. |

`design.md` is the single source of truth. It consolidates two earlier drafts — the scalar ranking (issue #2) and the domain-specific profile (issue #3) — into one method, and integrates the methodology critique tracked in issue #4. The scalar ranking and the profile are two **deliverables of one design**, not two designs.

### Naming discipline

- **Target-specific** dependability is `R_dep,t` (scalar) or the profile `(R^guide_t, R^donor_t, R^condition_t)`. It is *inspired by* G-theory, not a classical per-target coefficient.
- **Design-level** G-theory coefficients are `Eρ²` (relative / ranking) and `Φ` (absolute / hit-call) — one per measurement design, reported to characterize the design.
- We never write a per-target `Φ_t`. Classical `Φ` is design-level; the per-target number is `R_dep,t`.
