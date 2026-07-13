# ADR 0001 — Data tier boundary: research vs analysis vs demo

- **Status**: Accepted
- **Date**: 2026-07-13
- **Issue**: [#18](https://github.com/kiki830621/G-perturb/issues/18)
- **Related**: #5 (hackathon scope), #7 (data-size inventory), #17 (estimator methods)

## Context

The phrase "the complete data" has been used for three very different things: the
cell-level raw data, the AnnData/MuData matrices used for analysis, and the small
derived ranking the demo actually shows. A data-serving discussion asked whether
"the complete data is one giant table — could it just be hard-coded in a NestJS
project?" Without a frozen boundary, an implementer could mistake tens of GB of
analysis files, or ~1.6 TB of cell-level data, for something embeddable in an app.

"Hard-coded" itself was ambiguous, conflating two different things:

- **Not acceptable** — writing data as TypeScript object/array constants compiled
  into the server binary.
- **Acceptable** — the analysis pipeline emitting versioned JSON/CSV that a static
  site (or a backend) reads or streams; the data is an asset, not hand-written code.

This ADR freezes a three-tier contract so the demo layer picks the right storage and
serving model, and so no research file ever ends up in the repository, a build
artifact, or a Node.js heap.

## Decision

Three tiers, with distinct storage, formats, and rules.

### Tier A — research / raw (never in the app)

Cell-level H5AD/H5MU and the large analysis matrices. They live in research storage
or object storage, **never** in the application repository, a build artifact, a
container image, git history, or a Node.js heap.

### Tier B — analysis / materialized

Products of the analysis pipeline, kept as CSV/Parquet/JSON with an explicit schema,
version, and checksum. **Not** written as TypeScript constants. Tier B is an
intermediate: it can be re-sliced into Tier C, but it is not itself served to the UI.

### Tier C — product / demo

The minimal UI payload: only the fields the demo needs, as a versioned, verifiable,
small static artifact. **Default: a static site reads Tier C directly, with no live
backend.** A backend is added only when a concrete product need appears
(access control, server-side search/aggregation, audit, or dynamic updates).

## Measured size inventory

Sources: `README.md`, `analysis/data/DATA_AND_ASSUMPTIONS.md`,
`analysis/resolution/results/evidence.manifest.json`, and the actual file sizes under
`analysis/resolution/realdata/`.

| Tier | Layer | Shape / content | Size | Verdict |
|---|---|---:|---:|---|
| A | Cell-level raw | 12 × `assigned_guide.h5ad`, ~22M CD4+ T cells | ~1.6 TB (~110–161 GB each) | Never in the app or a backend |
| A/B | Joint pseudobulk | 278,684 obs × 18,129 genes (dense ≈ 5.05e9 cells) | 44,566,657,140 B (44.57 GB) | Research analysis only; read backed/sparse |
| A/B | Four core analysis files | joint, by-guide, by-donor, DE-stat variants | 107,643,600,588 B (107.64 GB **combined**, not one table) | Not a single website dataset; never in an app image |
| B | Design table | `design.csv`, 278,684 rows | 15,660,954 B (gzip ≈ 1,774,110 B) | Chunk/lazy-load only if a UI genuinely needs it |
| **C** | **Demo ranking + summaries** | overall, per-condition, context-specificity, summary | **see below** | **Versioned static artifact** |

**Tier C, measured 2026-07-13** (raw / gzip):

| File | Raw (B) | gzip (B) |
|---|---:|---:|
| `target_ranking.csv` | 823,731 | 267,314 |
| `target_ranking_percond.csv` | 2,535,292 | 685,897 |
| `target_context_specificity.csv` | 742,935 | 188,300 |
| `target_ranking_summary.json` | 5,431 | 1,195 |
| **Total** | **4,107,389 (≈ 4.11 MB)** | **1,142,706 (≈ 1.14 MB)** |

The 107.64 GB figure is the **combined** size of four analysis variants, **not** a
single table a website must load. The demo needs ~1.14 MB gzip — four orders of
magnitude smaller.

## Tier C output schema

Each Tier C artifact is accompanied by a manifest entry declaring:

- **fields**: the exact columns the UI consumes (e.g. `target`, `E_t`, `R_dep`,
  `S_t`, `rank_S`, `rank_E`, per-condition `R_dep`, context-specificity flags);
- **schema_version**: bumped on any field addition/removal/rename;
- **producer**: `analysis/resolution/realdata/per_target_ranking.py`;
- **source_commit** and **data_version**: the repo commit and the evidence-manifest
  data version the artifact was generated from;
- **checksum**: SHA-256 of the raw file, for integrity/cache validation.

## Prohibitions (enforced)

- No H5AD/H5MU in JS/TS source, a frontend bundle, a server image, or git history.
- No full array/matrix written as a TypeScript constant compiled with server code.
- No large research file loaded whole into a Node.js heap at startup.
- No Tier-A/B artifact served directly to the UI; the static demo reads **only**
  Tier C.

## If a backend is ever added

A backend is justified only by a concrete need (access control, server-side
search/aggregation, audit, dynamic updates). If added, it MUST:

- read external, versioned Tier C artifacts — never embed them as source constants;
- declare schema version, checksum/ETag, compression, and pagination/chunking;
- define a recovery strategy for a failed artifact update;
- ship an integration test proving the API does **not** load Tier A/B files at
  startup, supports compression and cache validation, and can recover from a
  versioned artifact.

That decision gets its own ADR (0002+), proving the need item by item.

## Enforcement

- `.gitignore` already blocks `*.h5ad`, `*.h5mu`, and `effect.f32` from tracking.
- `scripts/check-data-boundary.sh` is the automated guard: it fails if any
  H5AD/H5MU/large-matrix file is tracked, or if a Tier C artifact exceeds the frozen
  payload budget. Run it in CI and before publishing the demo.

## Consequences

Research keeps the full evidence trail; the demo stays small, reproducible,
cacheable, and replaceable. The ~1.14 MB gzip demo payload is served statically; a
backend is opt-in, not a default that adds ops surface without a product need.
