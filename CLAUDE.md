<!-- SPECTRA:START v1.0.2 -->

# Spectra Instructions

This project uses Spectra for Spec-Driven Development(SDD). Specs live in `openspec/specs/`, change proposals in `openspec/changes/`.

## Use `/spectra-*` skills when:

- A discussion needs structure before coding → `/spectra-discuss`
- User wants to plan, propose, or design a change → `/spectra-propose`
- Tasks are ready to implement → `/spectra-apply`
- There's an in-progress change to continue → `/spectra-ingest`
- User asks about specs or how something works → `/spectra-ask`
- Implementation is done → `/spectra-archive`
- Commit only files related to a specific change → `/spectra-commit`

## Workflow

discuss? → propose → apply ⇄ ingest → archive

- `discuss` is optional — skip if requirements are clear
- Requirements change mid-work? Plan mode → `ingest` → resume `apply`

## Parked Changes

Changes can be parked（暫存）— temporarily moved out of `openspec/changes/`. Parked changes won't appear in `spectra list` but can be found with `spectra list --parked`. To restore: `spectra unpark <name>`. The `/spectra-apply` and `/spectra-ingest` skills handle parked changes automatically.

<!-- SPECTRA:END -->

# CLAUDE.md — G-perturb

Working instructions for Claude Code on this project.

## Project

Reliability-weighted target ranking for T cell Perturb-seq via generalizability theory.
See [README.md](./README.md) for the full problem statement, method, and deliverable.
Built for **Built with Claude: Life Sciences** (Researcher track, 2026).

## Methodology standard — paper-grade, no compromise (CRITICAL, OVERRIDES ALL)

The statistical methodology is held to **paper-grade rigor with zero retreat, taken to the limit.**
The GPT-5.6 Sol adversarial red-team review
([`docs/reviews/sol-pass-b-adversarial-statistical-review.md`](./docs/reviews/sol-pass-b-adversarial-statistical-review.md),
verdict **blocked**; issues #9 / #10) defines the bar, and this bar is binding:

- **Resolve every P0 and P1 finding** (B-001 … B-011) before any method is declared *primary*. There is
  **no "hackathon cut", no "design-specified" shortcut, no degraded fallback presented as a result.**
  Deadline pressure does **not** lower the bar.
- **Freeze the falsification gates (review §7) and the required controls (review §8) BEFORE looking at
  any real target result** — Monte Carlo scale, type-I, FDR/false-sign, coverage, component recovery,
  winner's-curse calibration, D-study monotonicity, candidate-disagreement diagnosis, compute gates;
  NTC-vs-NTC, guide cross-fit, leave-one-donor-out, common-support sensitivity, external-evidence taxonomy.
- **Select the profile method only via pre-registered synthetic recovery** — never by K562 or any
  external-validation performance, never by which result looks nicer.
- **Identifiability fail-closed.** Any quantity not identifiable from the actual joint observation design
  (a run/interaction that adds no rank; a replication floor with no identical-spec replicate; a condition
  claim outside its common support) is reported `not_identifiable` / degraded / blocked — never fabricated,
  never zero-filled, never renamed to imply more than the data supports.
- **Prove before you name.** A distance-based attribution is **not** a variance component without a PSD +
  additivity proof; `1 − CCC` shares are diagnostics until proven. `not_identifiable` beats a pretty number.
- **Honest labeling.** K562 = cross-cell-type transportability (not "independent replication"); same-CD4
  pathway analysis = internal sensitivity (not validation); arrayed bulk/flow = assay translation.
- **New frozen evidence manifest first** (B-001): download the ~44.6 GB joint pseudobulk, audit the actual
  target×guide×donor×condition grid, missing cells, NTC coverage, and design-matrix rank; re-run affected
  blind passes. Marginal `h5mu` are comparison/degraded outputs only.

This standard **supersedes the hackathon-cut framing** everywhere they conflict. Tracked in #10; it drives
the `audit-complete-methodology` OpenSpec change, which gates #8's statistical core.

## Development workflow — Issue-Driven Development (IDD)

- **All work goes through IDD.** Every change starts from a GitHub issue in *this* repo.
- **Run IDD from inside this project.** IDD commands (`/idd-issue`, `/idd-diagnose`, …) must be
  invoked from within this repo so issues land in `kiki830621/G-perturb` — never in the parent
  `Academic` monorepo or anywhere else.
- Target-repo config lives in [`.claude/.idd/local.json`](./.claude/.idd/local.json)
  (`github_repo: kiki830621/G-perturb`).

## Hackathon compliance

- **New work only** — everything is built from scratch during the hackathon window
  (hacking opened 2026-07-07 12:30 PM ET). Repo scaffolding and all analysis were created after that.
- **Open source** — Apache-2.0. The repo is **private during development** and flips to
  **public before submission** (`gh repo edit kiki830621/G-perturb --visibility public`).
