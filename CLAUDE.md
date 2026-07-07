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
