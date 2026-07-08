#!/usr/bin/env python3
"""Build CODEBOOK.json for the released CD4+ T cell Perturb-seq summary statistics.

Reads the downloaded data in `raw/`:
  - supplementary CSVs (MB-scale): auto-profiled column-by-column (dtype, cardinality,
    missingness, example);
  - the large `.h5ad` / `.h5mu` products (GB-scale): the HDF5 STRUCTURE is read with
    h5py (`.obs` columns, `.layers` keys, `.mod` modalities, `n_obs`) — cheap, since
    only group metadata and the tiny `.obs` datasets are touched, never the genome-wide
    layers. Field meanings and G-theory facet roles come from the dataset's
    `data_sharing_readme.md`.

Only `guide_kd_efficiency` (on the companion GitHub repo, not this S3 bucket) remains
documented-but-not-downloaded.

Run:  python3 build_codebook.py      (writes CODEBOOK.json next to this script)

Source: Zhu et al. 2025, bioRxiv 2025.12.23.696273 (Marson & Pritchard labs),
CZI Virtual Cells, s3://genome-scale-tcell-perturb-seq/marson2025_data/
"""
from __future__ import annotations

import json
import os
import sys

try:
    import pandas as pd
except ImportError:
    sys.exit("build_codebook.py needs pandas (pip install pandas)")

try:
    import h5py
except ImportError:
    sys.exit("build_codebook.py needs h5py (pip install h5py) to read the .h5ad/.h5mu structure")

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "CODEBOOK.json")

# CSVs actually downloaded (MB-scale) — auto-profiled.
CSV_FILES = {
    "sample_metadata.suppl_table.csv": "Per-sample experimental metadata + donor demographics (one row per donor x condition x run).",
    "DE_stats.suppl_table.csv": "Per-(target x condition) differential-expression summary. REDUCED 16-col release: effect magnitude + basic QC only; reliability correlation fields are NOT here (see DE_stats.h5ad .obs).",
    "sgrna_library_metadata.suppl_table.csv": "Per-sgRNA guide library: genomic target, design, off-target neighbours (guide -> gene mapping; the guide facet's definition).",
}

# facet_role vocabulary: target | guide | donor | condition | effect | error | reliability | quality | id | design | demographic | meta
# Hand-authored from data_sharing_readme.md. Columns absent here are marked "unclassified".
FIELD_META = {
    # --- facets / ids ---
    "index": ("id", "Observation key `{target_contrast}_{culture_condition}`."),
    "target_condition": ("id", "Observation key `{target_contrast}_{culture_condition}` in the per-guide / per-donor-pair modalities."),
    "target_contrast": ("target", "Ensembl gene ID of the perturbed gene (object of measurement)."),
    "target_contrast_gene_name": ("target", "Symbol of the perturbed gene."),
    "culture_condition": ("condition", "Stimulation condition facet: Rest / Stim8hr / Stim48hr."),
    "donor_id": ("donor", "Donor facet identifier (4 donors)."),
    "guide_id": ("guide", "sgRNA guide facet identifier ('multi-guide' if >1 detected)."),
    "sgRNA": ("guide", "Unique sgRNA guide identifier (the guide facet)."),
    "cell_sample_id": ("id", "Unique biological sample identifier."),
    "10xrun_id": ("meta", "Processing batch / run identifier (R1 or R2)."),
    "library_id": ("id", "Sequencing library identifier (matches cellranger outputs)."),
    # --- effect magnitude (E_t) ---
    "ontarget_effect_size": ("effect", "Effect size of the perturbation on its intended target gene."),
    "n_total_de_genes": ("effect", "Total significantly DE genes at 10% FDR (a candidate E_t)."),
    "n_up_genes": ("effect", "Count of significantly upregulated genes (10% FDR)."),
    "n_down_genes": ("effect", "Count of significantly downregulated genes (10% FDR)."),
    "n_downstream": ("effect", "Downstream (trans) DE genes, excluding the on-target effect."),
    "target_baseMean": ("effect", "Mean baseline expression of the target gene."),
    "n_total_genes_category": ("effect", "Category based on number of trans-effects."),
    "ontarget_effect_category": ("effect", "Categorical label of on-target knockdown outcome."),
    # --- quality (Q_t) ---
    "ontarget_significant": ("quality", "On-target knockdown significant (10% FDR)?"),
    "offtarget_flag": ("quality", "Potential off-target effect flag (reduced-CSV consolidation of neighboring/distal flags)."),
    "n_cells_target": ("quality", "Number of cells with a targeting guide for this perturbation."),
    "chunk": ("meta", "DE processing group identifier."),
    # --- demographics (donor covariates) ---
    "age": ("demographic", "Donor age (years)."),
    "sex": ("demographic", "Donor sex."),
    "ethnicity": ("demographic", "Donor ethnicity."),
    # --- sgRNA design / off-target (feeds Q_t) ---
    "target_gene_id": ("guide", "Ensembl ID of the validated target gene for this guide."),
    "target_gene_name": ("guide", "Validated target gene symbol for this guide."),
    "designed_target_gene_name": ("design", "Intended target gene (as designed)."),
    "distance_to_closest_target_tss": ("design", "Distance (bp) from guide to the closest target TSS."),
    "putative_bidirectional_promoter": ("quality", "Guide may hit a bidirectional promoter (multi-gene risk)."),
    "chromosome": ("design", "Chromosome of the guide target site."),
    "seq": ("design", "Full guide RNA sequence."),
}

# Reliability / QC fields that live in DE_stats.h5ad .obs but NOT in the reduced CSV.
# (Merged with FIELD_META when documenting the h5ad's real .obs columns.)
H5_OBS_META = {
    "guide_correlation_all": ("reliability", "Pearson r between the two guides' per-gene DE z-scores, all genes. NaN if only one guide. -> first-pass R_guide."),
    "guide_correlation_signif": ("reliability", "Same guide correlation, restricted to significant DE genes."),
    "guide_correlation_all_pval": ("reliability", "p-value for guide_correlation_all."),
    "guide_correlation_signif_pval": ("reliability", "p-value for guide_correlation_signif."),
    "guide_n_signif_ontarget": ("quality", "Number of guides with a significant on-target effect."),
    "donor_correlation_all_mean": ("reliability", "Mean over donor-pair Pearson r of per-gene DE logFC (all genes). -> first-pass R_donor."),
    "donor_correlation_all_min": ("reliability", "Min over donor-pairs (conservative R_donor)."),
    "donor_correlation_hits_mean": ("reliability", "Mean cross-donor r on per-target hit genes."),
    "donor_correlation_hits_min": ("reliability", "Min cross-donor r on hit genes."),
    "n_guides": ("quality", "Number of guides aggregated into the per-target DE estimate."),
    "single_guide_estimate": ("quality", "DE estimate came from a single guide only."),
    "neighboring_gene_KD": ("quality", "Adjacent gene also knocked down (cis off-target)."),
    "distal_offtarget_flag": ("quality", "Potential distal off-target (predicted alignment + down-regulation)."),
    "low_target_gex": ("quality", "Target gene low baseline expression (KD estimate unreliable)."),
}

# .layers meaning (genome-wide per target x condition vectors). NOT read, only keyed.
H5_LAYER_META = {
    "log_fc": ("effect", "Log2 fold change (per perturbation x gene)."),
    "zscore": ("effect", "DE z-score = logFC / lfcSE (the effect-profile vector)."),
    "lfcSE": ("error", "Standard error of log fold change (the SE the G-study needs)."),
    "p_value": ("quality", "Raw DE p-value."),
    "adj_p_value": ("quality", "FDR-adjusted p-value."),
    "baseMean": ("effect", "Mean normalized expression per gene (DE baseline)."),
}

# Large HDF5 products now downloaded into raw/. Structure is read live; these give the
# semantic layer (why the product exists) + point to the field-meta dicts above.
H5_PRODUCTS = {
    "GWCD4i.DE_stats.h5ad": {
        "why": "Primary MVP driver. .obs holds the RELIABILITY fields absent from the reduced CSV; .layers holds the genome-wide effect vectors per target x condition.",
        "obs_meta": {**FIELD_META, **H5_OBS_META},
        "layer_meta": H5_LAYER_META,
    },
    "GWCD4i.DE_stats.by_guide.h5mu": {
        "why": "Per-guide DE effect vectors (one modality per guide) -> raw material to FIT the guide variance component, not just read a precomputed correlation.",
        "obs_meta": {**FIELD_META, **H5_OBS_META},
        "layer_meta": H5_LAYER_META,
    },
    "GWCD4i.DE_stats.by_donors.h5mu": {
        "why": "Per-donor-pair DE effect vectors (one modality per donor-pair) -> raw material to FIT the donor variance component.",
        "obs_meta": {**FIELD_META, **H5_OBS_META},
        "layer_meta": H5_LAYER_META,
    },
}

# Genuinely not on this S3 bucket (companion GitHub repo). Documented from the readme.
DEFERRED = {
    "guide_kd_efficiency.suppl_table.csv": {
        "size": "small (companion GitHub repo emdann/GWT_perturbseq_analysis_2025, NOT this S3 bucket)",
        "grain": "per sgRNA x condition",
        "why": "Per-guide knockdown efficiency (t-statistic vs NTC) -> feeds Q_t.",
        "key_fields": {
            "t_statistic": ("quality", "Welch t comparing guide vs NTC target expression (negative = knockdown)."),
            "signif_knockdown": ("quality", "Significant knockdown (adj_p < 0.1 and t < 0)."),
            "high_confidence_no_effect_guides": ("quality", "Guide with high-confidence no knockdown effect."),
        },
    },
}


def profile_series(s: "pd.Series") -> dict:
    dtype = str(s.dtype)
    non_null = s.dropna()
    example = None
    if len(non_null):
        example = non_null.iloc[0]
        if isinstance(example, str) and len(example) > 60:
            example = example[:57] + "..."
        example = example.item() if hasattr(example, "item") else example
    return {
        "dtype": dtype,
        "n_unique": int(s.nunique(dropna=True)),
        "n_missing": int(s.isna().sum()),
        "example": example,
    }


def build_csv_block(fname: str, desc: str) -> dict:
    df = pd.read_csv(os.path.join(RAW, fname), low_memory=False)
    fields = []
    for col in df.columns:
        role, description = FIELD_META.get(col, ("unclassified", None))
        fields.append({"name": col, "facet_role": role, "description": description, **profile_series(df[col])})
    return {"description": desc, "n_rows": int(len(df)), "n_cols": int(df.shape[1]), "fields": fields}


def _decode(x) -> str:
    return x.decode() if isinstance(x, (bytes, bytearray)) else str(x)


def inspect_h5(path: str) -> dict:
    """Read HDF5 structure only (group metadata + tiny .obs datasets), never the layers."""
    info: dict = {"size_bytes": os.path.getsize(path)}
    with h5py.File(path, "r") as h:
        top = list(h.keys())
        info["top_level_keys"] = top

        # Locate the anndata whose .obs/.layers we document. h5ad: root. h5mu: first /mod modality.
        if "mod" in h:  # .h5mu (muon) — modalities are separate anndatas
            mods = list(h["mod"].keys())
            info["modalities"] = mods
            adata = h["mod"][mods[0]] if mods else h
        else:  # .h5ad (anndata)
            adata = h

        obs = adata["obs"] if "obs" in adata else None
        if obs is not None:
            idx_key = _decode(obs.attrs.get("_index", "_index"))
            info["obs_columns"] = [k for k in obs.keys() if not k.startswith("_")]
            if idx_key in obs:
                node = obs[idx_key]
                # categorical index is a group (categories/codes); plain index is a dataset
                info["n_obs"] = int(node["codes"].shape[0]) if isinstance(node, h5py.Group) else int(node.shape[0])
        info["layers"] = list(adata["layers"].keys()) if "layers" in adata else []
    return info


def _fields_from(names: list, meta: dict) -> list:
    out = []
    for name in names:
        role, description = meta.get(name, ("unclassified", None))
        out.append({"name": name, "facet_role": role, "description": description})
    return out


def build_h5_block(prod: str, spec: dict) -> dict:
    path = os.path.join(RAW, prod)
    if not os.path.exists(path):
        return {"downloaded": False, "why_needed": spec["why"], "note": "file not present in raw/"}
    info = inspect_h5(path)
    gb = info["size_bytes"] / 1e9
    block = {
        "downloaded": True,
        "size_bytes": info["size_bytes"],
        "size": f"{gb:.2f} GB",
        "why_needed": spec["why"],
        "top_level_keys": info["top_level_keys"],
    }
    if "n_obs" in info:
        block["n_obs"] = info["n_obs"]
    if "modalities" in info:
        block["modalities"] = info["modalities"]
        block["grain"] = f"{len(info['modalities'])} modalities, each (target x condition)"
    else:
        block["grain"] = "(target x condition)"
    if info.get("obs_columns"):
        block["obs_fields"] = _fields_from(info["obs_columns"], spec["obs_meta"])
    if info.get("layers"):
        block["layer_fields"] = _fields_from(info["layers"], spec["layer_meta"])
    return block


def build_deferred_block() -> dict:
    out = {}
    for prod, info in DEFERRED.items():
        out[prod] = {
            "downloaded": False,
            "size": info["size"],
            "grain": info["grain"],
            "why_needed": info["why"],
            "documented_fields": _fields_from(list(info["key_fields"]), info["key_fields"]),
        }
    return out


def main() -> None:
    if not os.path.isdir(RAW):
        sys.exit(f"raw/ not found ({RAW}); run fetch_data.sh first")

    codebook = {
        "dataset": {
            "name": "Genome-scale Perturb-seq in primary human CD4+ T cells",
            "citation": "Zhu, Dann, Yan, Reyes Retana, Goto, Guitche, Petersen, Ota, Pritchard, Marson (2025). bioRxiv 2025.12.23.696273.",
            "labs": "Marson & Pritchard",
            "platform": "genome-scale CRISPRi Perturb-seq",
            "n_cells_approx": 22_000_000,
            "n_donors": 4,
            "conditions": ["Rest", "Stim8hr", "Stim48hr"],
            "s3": "s3://genome-scale-tcell-perturb-seq/marson2025_data/",
            "geo": "GSE314342 / SRP643211 (raw reads)",
            "note": "Field descriptions from data_sharing_readme.md; CSV profiles and .h5ad/.h5mu structure read from the actual downloaded files.",
        },
        "facet_design": {
            "target": {"role": "object of measurement", "source": "target_contrast (DE_stats)", "n": "~12,748 genes"},
            "guide": {"role": "parallel-forms facet", "available": True,
                      "source": "guide_id (cell .obs) / sgRNA (library) / by_guide.h5mu modalities",
                      "n_per_gene": "~2 (targets with 1 passing guide flagged single_guide_estimate)"},
            "donor": {"role": "occasion facet", "available": True, "source": "donor_id / by_donors.h5mu modalities", "n_levels": 4},
            "condition": {"role": "crossed context facet (biology, not just error)", "available": True,
                          "source": "culture_condition", "n_levels": 3,
                          "note": "Fixed facet: report both cross-condition (broad) and within-condition (context-specific) dependability."},
            "effect_and_SE": {"logFC/zscore": "DE_stats.h5ad .layers (log_fc, zscore)",
                              "SE": "lfcSE (.layers)",
                              "reliability_correlations": "DE_stats.h5ad .obs (guide_correlation_*, donor_correlation_*) — NOT in the flat CSV"},
        },
        "known_gaps": [
            "DE_stats.suppl_table.csv is a reduced 16-col release: it lacks guide_correlation_*, donor_correlation_*, n_guides, single_guide_estimate, neighboring_gene_KD, distal_offtarget_flag. Those live in GWCD4i.DE_stats.h5ad .obs (now downloaded).",
            "guide_kd_efficiency + several suppl tables are on the companion GitHub repo (emdann/GWT_perturbseq_analysis_2025), not this S3 bucket — the only product not downloaded.",
            "Two guides / four donors -> per-target variance components under-identified; the full G-study uses partial-pooling REML (see docs/design.md / issue #2).",
        ],
        "files_downloaded": {fname: build_csv_block(fname, desc) for fname, desc in CSV_FILES.items()},
        "h5_products_downloaded": {prod: build_h5_block(prod, spec) for prod, spec in H5_PRODUCTS.items()},
        "products_not_downloaded": build_deferred_block(),
    }

    with open(OUT, "w") as f:
        json.dump(codebook, f, indent=2, ensure_ascii=False)

    n_csv_cols = sum(b["n_cols"] for b in codebook["files_downloaded"].values())
    n_h5_fields = sum(len(b.get("obs_fields", [])) + len(b.get("layer_fields", []))
                      for b in codebook["h5_products_downloaded"].values())
    print(f"wrote {OUT}")
    print(f"  {len(codebook['files_downloaded'])} CSVs, {n_csv_cols} documented columns")
    print(f"  {len(codebook['h5_products_downloaded'])} h5 products downloaded, {n_h5_fields} obs+layer fields documented")
    print(f"  {len(codebook['products_not_downloaded'])} product still deferred (companion GitHub repo)")


if __name__ == "__main__":
    main()
