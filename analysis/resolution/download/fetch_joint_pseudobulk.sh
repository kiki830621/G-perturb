#!/usr/bin/env bash
# fetch_joint_pseudobulk.sh  —  task 1.1: download the JOINT pseudobulk and verify it.
#
# RESOLVED (2026-07, B-001 Open Question closed): the joint guide×donor×condition pseudobulk is
#   GWCD4i.pseudobulk_merged.h5ad   (44,566,657,140 bytes = 44.6 GB, n_vars=18,129)
# on the public S3 bucket s3://genome-scale-tcell-perturb-seq/marson2025_data/ (Zhu et al. 2025,
# bioRxiv 2025.12.23.696273, Marson & Pritchard labs). No credentials; HTTPS mirror. Because it is
# large it lands in analysis/data/raw/ (gitignored), not the repo tree; the download itself does not
# require the Academia Sinica network — only the heavy Monte-Carlo compute does.
#
# The canonical, resumable fetcher is analysis/data/fetch_data.sh --joint (curl -C -). This script
# delegates to it so there is one source of truth for the URL and resume logic.
#
# Usage:
#   ./fetch_joint_pseudobulk.sh            # delegates to fetch_data.sh --joint (resumable)
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_FETCH="$(cd "$HERE/../../data" && pwd)/fetch_data.sh"
RAW="$(cd "$HERE/../../data" && pwd)/raw"
EXPECT_BYTES=44566657140
target="$RAW/GWCD4i.pseudobulk_merged.h5ad"

echo "[fetch] joint pseudobulk via $DATA_FETCH --joint"
bash "$DATA_FETCH" --joint

# integrity: confirm the full expected byte count landed (B-001 requires a verified manifest input)
if [[ -f "$target" ]]; then
  got=$(stat -f%z "$target" 2>/dev/null || stat -c%s "$target")
  if [[ "$got" == "$EXPECT_BYTES" ]]; then
    echo "[verify] OK — $got bytes"
    echo "[next] python3 ../manifest/build_manifest.py --joint $target"
  else
    echo "[verify] INCOMPLETE — $got / $EXPECT_BYTES bytes; re-run to resume (curl -C -)"; exit 3
  fi
else
  echo "FAIL-CLOSED: $target not present after fetch"; exit 2
fi
