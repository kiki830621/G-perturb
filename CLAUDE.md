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
