#!/usr/bin/env bash
# Fetch the released CD4+ T cell Perturb-seq summary statistics into raw/ (gitignored).
#
# Source: Zhu et al. 2025, bioRxiv 2025.12.23.696273 (Marson & Pritchard labs, CZI).
# Public S3 bucket, no credentials. Uses the HTTPS endpoint so no AWS CLI is required.
#
# Usage:
#   bash fetch_data.sh            # MB-scale CSVs only (default; ~14 MB)
#   bash fetch_data.sh --h5ad     # + GWCD4i.DE_stats.h5ad  (15.6 GB — reliability fields)
#   bash fetch_data.sh --h5mu     # + by_guide + by_donors h5mu (27 + 15.7 GB — variance model)
set -euo pipefail

BASE="https://genome-scale-tcell-perturb-seq.s3.amazonaws.com/marson2025_data"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAW="$HERE/raw"
mkdir -p "$RAW"

get() {  # get <relative-path> <local-name>
  local url="$BASE/$1" out="$RAW/$2"
  echo "→ $2"
  curl -fSL --retry 3 -o "$out" "$url"
}

echo "== MB-scale summary statistics (always) =="
get "data_sharing_readme.md"                          "data_sharing_readme.md"
get "suppl_tables/sample_metadata.suppl_table.csv"    "sample_metadata.suppl_table.csv"
get "suppl_tables/DE_stats.suppl_table.csv"           "DE_stats.suppl_table.csv"
get "suppl_tables/sgrna_library_metadata.suppl_table.csv" "sgrna_library_metadata.suppl_table.csv"

# guide_kd_efficiency.suppl_table.csv + several other suppl tables are NOT in this S3
# bucket — they are on the companion GitHub repo emdann/GWT_perturbseq_analysis_2025.

for arg in "$@"; do
  case "$arg" in
    --h5ad)
      echo "== DE_stats.h5ad (15.6 GB — reliability correlation fields in .obs) =="
      get "GWCD4i.DE_stats.h5ad" "GWCD4i.DE_stats.h5ad" ;;
    --h5mu)
      echo "== per-facet h5mu (27 + 15.7 GB — raw guide-/donor-resolved effect vectors) =="
      get "GWCD4i.DE_stats.by_guide.h5mu"  "GWCD4i.DE_stats.by_guide.h5mu"
      get "GWCD4i.DE_stats.by_donors.h5mu" "GWCD4i.DE_stats.by_donors.h5mu" ;;
    *) echo "⚠ unknown flag: $arg (use --h5ad / --h5mu)" >&2 ;;
  esac
done

# NEVER download the cell-level files: D*_*.assigned_guide.h5ad ×12, 110-161 GB each (~1.6 TB).
echo "done. Next: python3 build_codebook.py && python3 validate_codebook.py"
