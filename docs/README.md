# Design docs

The scientific design for G-perturb, captured as it evolved. Two **complementary** framings are on the table; both feed the same generalizability-theory machinery (the crossed `T × G × D × C` variance decomposition), and differ only in how they report per-target dependability.

| Doc | Framing | Output | Tracked in |
|---|---|---|---|
| [`design.md`](./design.md) | Reliability-weighted ranking — collapse dependability to a scalar `R_dep,t` | a re-ranked target list (`Priority_t = Effect_t × R_dep,t × Q_t`) + disagreement table | [#2](https://github.com/kiki830621/G-perturb/issues/2) |
| [`design_domain_specific.md`](./design_domain_specific.md) | Domain-specific generalizability — keep dependability as a per-target vector `(R^guide, R^donor, R^condition)` | a generalizability *profile* / evidence map + diagnostic typology (guide-fragile / donor-fragile / context-specific / broadly dependable) | [#3](https://github.com/kiki830621/G-perturb/issues/3) |

Both share one naming discipline: **target-specific** scores are empirical `R_dep` / `R^domain`; **design-level** coefficients are `Eρ²` (relative decisions) and `Φ` (absolute decisions). Neither claims a classical per-target `Φ_t` — classical `Φ` is a property of a measurement *design*, not of a single target.

`design.md` is the earlier scalar framing; `design_domain_specific.md` refines it into a profile. Per the project author, both are worth keeping: the ranking (#2) and the diagnostic map (#3) answer different questions. Which (if either) becomes canonical is decided during modeling.
