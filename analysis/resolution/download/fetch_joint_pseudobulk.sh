#!/usr/bin/env bash
# fetch_joint_pseudobulk.sh  —  task 1.1: download the ~44.6 GB JOINT pseudobulk and verify it.
#
# The joint target x guide x donor x condition pseudobulk is the minimum data unit for the complete
# decomposition (B-001). Marginal by_guide.h5mu / by_donors.h5mu are already local (#7) and are NOT
# a substitute. Because it is large, it goes to cluster storage, not the repo working tree.
#
# Source resolution (fill JOINT_URL once confirmed):
#   - companion analysis repo: github.com/emdann/GWT_perturbseq_analysis_2025 (data-availability section)
#   - Zhu et al. 2025 CD4+ Perturb-seq GEO/Zenodo record (the study's primary deposit)
# The exact record + file split are an Open Question in design.md; resolve, then set JOINT_URL.
#
# Usage:
#   JOINT_URL="https://.../joint_pseudobulk.h5ad" DEST=/path/on/cluster/NA ./fetch_joint_pseudobulk.sh
set -euo pipefail

JOINT_URL="${JOINT_URL:-}"
DEST="${DEST:-$HOME/NA/gperturb/joint}"
EXPECT_SHA256="${EXPECT_SHA256:-}"     # set once known, to verify integrity (B-001)

if [[ -z "$JOINT_URL" ]]; then
  echo "FAIL-CLOSED: JOINT_URL is unset."
  echo "  Resolve the joint-pseudobulk record (companion repo data-availability / GEO / Zenodo),"
  echo "  then re-run:  JOINT_URL=<url> DEST=<cluster path> $0"
  echo "  Do NOT proceed with marginal by_guide/by_donors as a stand-in."
  exit 2
fi

mkdir -p "$DEST"
fname="$(basename "${JOINT_URL%%\?*}")"
out="$DEST/$fname"
echo "[fetch] $JOINT_URL"
echo "[fetch] -> $out"
# resumable download; on the stat cluster prefer running this inside a qsub job, not the front-end
curl -fL --retry 5 -C - -o "$out" "$JOINT_URL"

if [[ -n "$EXPECT_SHA256" ]]; then
  echo "[verify] sha256..."
  got="$(shasum -a 256 "$out" | awk '{print $1}')"
  if [[ "$got" != "$EXPECT_SHA256" ]]; then
    echo "FAIL-CLOSED: checksum mismatch (got $got, expected $EXPECT_SHA256)"; exit 3
  fi
  echo "[verify] OK $got"
else
  shasum -a 256 "$out" | tee "$out.sha256"
  echo "[verify] recorded sha256 (no EXPECT_SHA256 provided to check against)"
fi
echo "[done] joint pseudobulk at $out — next: manifest/build_manifest.py --joint $out"
