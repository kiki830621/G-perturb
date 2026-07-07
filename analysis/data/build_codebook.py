#!/usr/bin/env python3
"""Build CODEBOOK.json for the released CD4+ T cell Perturb-seq summary statistics.

Reads the downloaded supplementary CSVs in `raw/`, auto-profiles every column
(dtype, cardinality, missingness, example), merges hand-authored descriptions and
G-theory facet roles from the dataset's `data_sharing_readme.md`, and documents the
larger `.h5ad` / `.h5mu` products (not downloaded) from the readme field dictionary —
including the reliability fields that are NOT in the flat CSV.

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

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "CODEBOOK.json")

# CSVs actually downloaded (MB-scale). Big .h5ad/.h5mu are documented, not read.
CSV_FILES = {
    "sample_metadata.suppl_table.csv": "Per-sample experimental metadata + donor demographics (one row per donor x condition x run).",
    "DE_stats.suppl_table.csv": "Per-(target x condition) differential-expression summary. REDUCED 16-col release: effect magnitude + basic QC only; reliability correlation fields are NOT here (see DE_stats.h5ad .obs).",
    "sgrna_library_metadata.suppl_table.csv": "Per-sgRNA guide library: genomic target, design, off-target neighbours (guide -> gene mapping; the guide facet's definition).",
}

# facet_role vocabulary: target | guide | donor | condition | effect | error | reliability | quality | id | design | demographic | meta
# Hand-authored from data_sharing_readme.md. Columns absent here are auto-profiled with role "unclassified".
FIELD_META = {
    # --- facets / ids ---
    "index": ("id", "Observation key `{target_contrast}_{culture_condition}`."),
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

# Fields NOT in the downloaded CSVs — documented from the readme so the codebook is
# complete for the modelling (issue #2). Grouped by their source product.
PRODUCTS_NOT_DOWNLOADED = {
    "GWCD4i.DE_stats.h5ad": {
        "size": "15.6 GB",
        "grain": "(target x condition), .obs = 33,983 rows",
        "why": "Holds the RELIABILITY fields absent from DE_stats.suppl_table.csv. Needed even for the heuristic MVP R_t.",
        "key_fields": {
            "guide_correlation_all": ("reliability", "Pearson r between the two guides' per-gene DE z-scores, all genes. NaN if only one guide. -> R_guide."),
            "guide_correlation_signif": ("reliability", "Same, restricted to significant DE genes."),
            "donor_correlation_all_mean": ("reliability", "Mean over donor-pair Pearson r of per-gene DE logFC (all genes). -> R_donor."),
            "donor_correlation_all_min": ("reliability", "Min over donor-pairs (conservative R_donor)."),
            "donor_correlation_hits_mean": ("reliability", "Mean cross-donor r on per-target hit genes."),
            "donor_correlation_hits_min": ("reliability", "Min cross-donor r on hit genes."),
            "n_guides": ("quality", "Number of guides aggregated into the per-target DE estimate."),
            "single_guide_estimate": ("quality", "DE estimate came from a single guide only."),
            "neighboring_gene_KD": ("quality", "Adjacent gene also knocked down (cis off-target)."),
            "distal_offtarget_flag": ("quality", "Potential distal off-target (predicted alignment + down-regulation)."),
            "low_target_gex": ("quality", "Target gene low baseline expression (KD estimate unreliable)."),
        },
        "layers": {
            "log_fc": ("effect", "Log2 fold change (per perturbation x gene)."),
            "zscore": ("effect", "DE z-score = logFC / lfcSE."),
            "lfcSE": ("error", "Standard error of log fold change (the SE the G-study needs)."),
            "adj_p_value": ("quality", "FDR-adjusted p-value."),
        },
    },
    "GWCD4i.DE_stats.by_guide.h5mu": {
        "size": "27 GB",
        "grain": "modalities guide_1 / guide_2, each (target x condition)",
        "why": "Per-guide DE effect vectors -> raw material to FIT the guide variance component (not just a precomputed correlation).",
        "key_fields": {},
        "layers": {"zscore": ("effect", "Per-guide DE z-score; same schema as DE_stats.h5ad.")},
    },
    "GWCD4i.DE_stats.by_donors.h5mu": {
        "size": "15.7 GB",
        "grain": "one modality per donor-pair, each (target x condition)",
        "why": "Per-donor-pair DE effect vectors -> raw material to FIT the donor variance component.",
        "key_fields": {},
        "layers": {"zscore": ("effect", "Per-donor-pair DE z-score; same schema as DE_stats.h5ad.")},
    },
    "guide_kd_efficiency.suppl_table.csv": {
        "size": "small (companion GitHub repo emdann/GWT_perturbseq_analysis_2025, NOT this S3 bucket)",
        "grain": "per sgRNA x condition",
        "why": "Per-guide knockdown efficiency (t-statistic vs NTC) -> feeds Q_t.",
        "key_fields": {
            "t_statistic": ("quality", "Welch t comparing guide vs NTC target expression (negative = knockdown)."),
            "signif_knockdown": ("quality", "Significant knockdown (adj_p < 0.1 and t < 0)."),
            "high_confidence_no_effect_guides": ("quality", "Guide with high-confidence no knockdown effect."),
        },
        "layers": {},
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


def build_file_block(fname: str, desc: str) -> dict:
    path = os.path.join(RAW, fname)
    df = pd.read_csv(path, low_memory=False)
    fields = []
    for col in df.columns:
        role, description = FIELD_META.get(col, ("unclassified", None))
        prof = profile_series(df[col])
        fields.append({
            "name": col,
            "facet_role": role,
            "description": description,
            **prof,
        })
    return {
        "description": desc,
        "n_rows": int(len(df)),
        "n_cols": int(df.shape[1]),
        "fields": fields,
    }


def build_products_block() -> dict:
    out = {}
    for prod, info in PRODUCTS_NOT_DOWNLOADED.items():
        fields = []
        for col, (role, description) in {**info["key_fields"], **info["layers"]}.items():
            fields.append({"name": col, "facet_role": role, "description": description})
        out[prod] = {
            "downloaded": False,
            "size": info["size"],
            "grain": info["grain"],
            "why_needed": info["why"],
            "documented_fields": fields,
        }
    return out


def main():
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
            "note": "Field descriptions taken from the dataset's data_sharing_readme.md; profiles from the actual downloaded CSVs.",
        },
        "facet_design": {
            "target": {"role": "object of measurement", "source": "target_contrast (DE_stats)", "n": "~12,748 genes"},
            "guide": {"role": "parallel-forms facet", "available": True,
                      "source": "guide_id (cell .obs) / sgRNA (library) / by_guide.h5mu modalities",
                      "n_per_gene": "~2 (targets with 1 passing guide flagged single_guide_estimate)"},
            "donor": {"role": "occasion facet", "available": True, "source": "donor_id", "n_levels": 4},
            "condition": {"role": "crossed context facet (biology, not just error)", "available": True,
                          "source": "culture_condition", "n_levels": 3,
                          "note": "Two rankings planned: global (condition random) vs context-specific (condition fixed)."},
            "effect_and_SE": {"logFC/zscore": "DE_stats.h5ad .layers (log_fc, zscore)",
                              "SE": "lfcSE (.layers)",
                              "reliability_correlations": "DE_stats.h5ad .obs (guide_correlation_*, donor_correlation_*) — NOT in the flat CSV"},
        },
        "known_gaps": [
            "DE_stats.suppl_table.csv is a reduced 16-col release: it lacks guide_correlation_*, donor_correlation_*, n_guides, single_guide_estimate, neighboring_gene_KD, distal_offtarget_flag. Those live in GWCD4i.DE_stats.h5ad .obs (15.6 GB).",
            "guide_kd_efficiency + several suppl tables are on the companion GitHub repo (emdann/GWT_perturbseq_analysis_2025), not this S3 bucket.",
            "Two guides / four donors -> per-target variance components under-identified; the full G-study uses partial-pooling REML (see repo README / issue #2).",
        ],
        "files_downloaded": {fname: build_file_block(fname, desc) for fname, desc in CSV_FILES.items()},
        "products_not_downloaded": build_products_block(),
    }

    with open(OUT, "w") as f:
        json.dump(codebook, f, indent=2, ensure_ascii=False)
    n_fields = sum(b["n_cols"] for b in codebook["files_downloaded"].values())
    print(f"wrote {OUT}")
    print(f"  {len(codebook['files_downloaded'])} CSVs, {n_fields} documented columns")
    print(f"  {len(codebook['products_not_downloaded'])} deferred products documented")


if __name__ == "__main__":
    main()
