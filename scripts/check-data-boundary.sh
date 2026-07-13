#!/usr/bin/env bash
# check-data-boundary.sh — enforce the Tier A/B/C data boundary (ADR 0001, issue #18).
#
# Fails (exit 1) if:
#   (1) any Tier-A file (H5AD/H5MU/*.f32/large matrix) is TRACKED in git, or
#   (2) any tracked file exceeds the large-file threshold (accidental data commit), or
#   (3) the Tier C demo payload exceeds its frozen budget.
#
# Run in CI and before publishing the demo. Read-only; never edits or deletes.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

fail=0
note() { printf '  %s\n' "$1"; }
err()  { printf '✗ %s\n' "$1"; fail=1; }

echo "== Tier boundary guard (ADR 0001, #18) =="

# (1) No Tier-A research artifacts tracked in git.
TIER_A_TRACKED=$(git ls-files | grep -iE '\.(h5ad|h5mu|f32)$' || true)
if [ -n "$TIER_A_TRACKED" ]; then
  err "Tier-A research artifacts are tracked in git (must stay in research/object storage):"
  printf '%s\n' "$TIER_A_TRACKED" | sed 's/^/    /'
else
  note "ok: no H5AD/H5MU/.f32 tracked in git"
fi

# (2) No accidentally-committed large file (research data must never land in the repo).
#     Threshold 20 MB — Tier C is ~4 MB; anything larger is a Tier-A/B leak or a stray asset.
LIMIT=$((20 * 1024 * 1024))
BIG=$(git ls-files | while read -r f; do
        [ -f "$f" ] || continue
        sz=$(wc -c <"$f")
        [ "$sz" -gt "$LIMIT" ] && printf '%s\t%d\n' "$f" "$sz"
      done || true)
if [ -n "$BIG" ]; then
  err "tracked file(s) exceed the ${LIMIT}-byte large-file limit (possible Tier-A/B leak):"
  printf '%s\n' "$BIG" | sed 's/^/    /'
else
  note "ok: no tracked file over $((LIMIT/1024/1024)) MB"
fi

# (3) Tier C demo payload within its frozen budget.
#     Frozen 2026-07-13: measured raw total 4,107,389 B; budget 6 MB raw gives headroom
#     for schema growth without ever regressing to TypeScript constants.
TIER_C_DIR="analysis/resolution/realdata"
TIER_C=(target_ranking.csv target_ranking_percond.csv target_context_specificity.csv target_ranking_summary.json)
BUDGET=$((6 * 1024 * 1024))
total=0; present=0
for f in "${TIER_C[@]}"; do
  p="$TIER_C_DIR/$f"
  if [ -f "$p" ]; then present=$((present+1)); total=$((total + $(wc -c <"$p"))); fi
done
if [ "$present" -eq 0 ]; then
  note "skip: no Tier C artifacts present (run per_target_ranking.py to generate)"
elif [ "$total" -gt "$BUDGET" ]; then
  err "Tier C payload ${total} B exceeds the ${BUDGET}-byte budget — field-slice/chunk/lazy-load, do NOT inline as constants."
else
  note "ok: Tier C payload ${total} B within ${BUDGET}-byte budget (${present}/${#TIER_C[@]} artifacts present)"
fi

echo "=========================================="
if [ "$fail" -ne 0 ]; then
  echo "FAIL — see ADR docs/decisions/0001-data-tier-boundary.md"
  exit 1
fi
echo "PASS"
