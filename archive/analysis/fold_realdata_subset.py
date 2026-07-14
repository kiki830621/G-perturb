#!/usr/bin/env python3
"""fold_realdata_subset.py  —  issue #20 step (a): does the count-fold effect change the target
ranking on REAL data, and does it de-attenuate sparse-but-strong targets? (subset, de-risk)

Two per-target magnitudes over a gene subset, from the real pseudobulk:
  M_t (plug-in)  : the shipped effect. Per obs, log1p(count/tc*1e6) minus the matched-stratum NTC
                   mean-log1p; averaged over the target's pseudobulks per gene; RMS over genes.
  M_t (count-fold): pool the target's counts per gene across all its pseudobulks (guide x donor x
                   condition), pool the NTC counts per gene; fold = log(pooled target rate / pooled
                   NTC rate) with a 0.5-count guard only for exact zeros; RMS over genes.

The count-fold's advantage appears at the POOLED (target) level: the plug-in averages logs of single
low-count pseudobulks (Jensen-attenuated, coverage-dependent), while the fold takes the log of the
pooled rate (near-unbiased). So a strong-but-sparse target, whose plug-in magnitude was shrunk by low
coverage, should RISE under the count-fold. The smoking gun is a negative correlation between a
target's coverage and its rank change (low coverage -> rank improves under the fold).

  env FR_NGENES (default 2500)  FR_SEED (default 0)
Reads the real pseudobulk; writes results/synthetic_recovery/fold_realdata_subset.json.
"""
import json
import os
import time

import h5py
import numpy as np
from scipy.sparse import csr_matrix, csc_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
H5 = os.path.join(HERE, "..", "..", "data", "raw", "GWCD4i.pseudobulk_merged.h5ad")
NGENES = int(os.environ.get("FR_NGENES", "2500"))
SEED = int(os.environ.get("FR_SEED", "0"))
t0 = time.time()


def log(m: str) -> None:
    print(f"[{time.time() - t0:6.1f}s] {m}", flush=True)


def cat(obs: h5py.Group, c: str) -> np.ndarray:
    g = obs[c]
    cats = [x.decode() if isinstance(x, bytes) else str(x) for x in g["categories"][:]]
    return np.array([cats[i] if i >= 0 else "" for i in g["codes"][:]], dtype=object)


def main() -> None:
    f = h5py.File(H5, "r")
    obs = f["obs"]
    tc = obs["total_counts"][:].astype(np.float64)
    n_cells = obs["n_cells"][:].astype(np.float64)
    n_obs = len(tc)
    donor, cond, run = cat(obs, "donor_id"), cat(obs, "culture_condition"), cat(obs, "10xrun_id")
    gtype = cat(obs, "guide_type")
    target_name = cat(obs, "perturbed_gene_name")
    ntc = gtype == "non-targeting"
    # target codes for the TARGETING perturbations only (NTC excluded from targets)
    is_pert = ~ntc
    uniq_t, tcode_full = np.unique(target_name[is_pert], return_inverse=True)
    n_target = len(uniq_t)
    log(f"n_obs={n_obs} n_target={n_target} ntc={int(ntc.sum())}")

    # stratum (donor,cond,run)
    strata: dict = {}
    stratum = np.empty(n_obs, np.int32)
    for i in range(n_obs):
        k = (donor[i], cond[i], run[i])
        stratum[i] = strata.setdefault(k, len(strata))
    n_strata = len(strata)

    # gene subset
    n_gene_all = f["var"]["_index"].shape[0]
    rng = np.random.default_rng(SEED)
    gsub = np.sort(rng.choice(n_gene_all, size=min(NGENES, n_gene_all), replace=False))
    log(f"loading X (CSR) and slicing {len(gsub)} genes...")
    X = f["X"]
    Xcsr = csr_matrix((X["data"][:], X["indices"][:], X["indptr"][:]), shape=(n_obs, n_gene_all))
    f.close()
    C = np.asarray(Xcsr[:, gsub].todense(), dtype=np.float64)  # n_obs x n_gene (counts)
    del Xcsr
    log(f"count submatrix {C.shape} ready")

    # ---- plug-in per-target magnitude ----
    cpm = np.log1p(C / tc[:, None] * 1e6)  # per-obs log1p CPM
    # NTC mean-log1p per stratum
    ntc_ref = np.zeros((n_strata, C.shape[1]))
    for s in range(n_strata):
        idx = np.where(ntc & (stratum == s))[0]
        ntc_ref[s] = cpm[idx].mean(0) if len(idx) else 0.0
    plug_eff = cpm - ntc_ref[stratum]  # per-obs effect
    del cpm
    # per-target mean over its pseudobulks, then RMS over genes
    # indicator (n_target x n_pert_obs) via bincount-style accumulation
    pert_rows = np.where(is_pert)[0]
    Tind = csr_matrix((np.ones(len(pert_rows)), (tcode_full, np.arange(len(pert_rows)))),
                      shape=(n_target, len(pert_rows)))
    cnt_t = np.asarray(Tind.sum(1)).ravel()  # pseudobulks per target
    prof_plug = np.asarray(Tind @ plug_eff[pert_rows]) / cnt_t[:, None]
    M_plug = np.sqrt((prof_plug ** 2).mean(1))
    del plug_eff, prof_plug

    # ---- count-fold per-target magnitude (pool counts per gene) ----
    pooled_ct = np.asarray(Tind @ C[pert_rows])          # n_target x n_gene summed counts
    pooled_tc = np.asarray(Tind @ tc[pert_rows][:, None]).ravel()  # n_target summed library size
    ntc_ct = C[ntc].sum(0)                                # n_gene summed NTC counts
    ntc_tc = tc[ntc].sum()
    rate_t = (pooled_ct + 0.5) / pooled_tc[:, None]
    rate_ntc = (ntc_ct + 0.5) / ntc_tc
    prof_fold = np.log(rate_t) - np.log(rate_ntc)         # count-fold profile per target x gene
    M_fold = np.sqrt((prof_fold ** 2).mean(1))            # naive (unweighted) magnitude
    # precision-weighted magnitude: w = inverse delta-method variance of the log-fold per gene
    # = 1 / (1/pooled_ct + 1/ntc_ct); low-count genes (noise) get low weight, so they cannot inflate
    w = 1.0 / (1.0 / (pooled_ct + 0.5) + 1.0 / (ntc_ct + 0.5))   # n_target x n_gene = precision = 1/SE^2
    M_fold_pw = np.sqrt((w * prof_fold ** 2).sum(1) / w.sum(1))
    # empirical-Bayes LFC shrinkage (apeglm-lite: normal prior N(0, tau2), global tau2 by moments):
    #   shrunk_LFC = LFC * tau2 / (tau2 + SE^2); low-count (high SE^2) genes shrink toward 0 but stay in.
    # This is the modern replacement for BOTH the naive fold and zero-inflation (user's #20 suggestion).
    se2 = 1.0 / w
    # robust global tau2 estimated by PRECISION-WEIGHTED moments, so the unbounded low-count folds
    # (which are the very noise we want to shrink) cannot corrupt the prior-variance estimate.
    Wsum = float(w.sum())
    tau2 = max(1e-6, float((w * prof_fold ** 2).sum()) / Wsum - prof_fold.size / Wsum)
    lfc_shrunk = prof_fold * (tau2 / (tau2 + se2))
    M_shrink = np.sqrt((lfc_shrunk ** 2).mean(1))
    # noise share: fraction of each target's naive magnitude^2 coming from low-count genes (pooled<5)
    noise_share = ((prof_fold ** 2) * (pooled_ct < 5)).sum(1) / (prof_fold ** 2).sum(1)
    del C, pooled_ct, w, se2, lfc_shrunk

    # coverage + rankings for naive fold AND precision-weighted fold
    cov_t = np.asarray(Tind @ n_cells[pert_rows][:, None]).ravel()
    def ranks(m):  # rank 0 = largest magnitude
        return (-m).argsort().argsort()
    def spear(a, b):
        return float(np.corrcoef(a, b)[0, 1])
    def topK(m, k=100):
        return set((-m).argsort()[:k])
    r_plug, r_fold, r_fold_pw, r_shrink = ranks(M_plug), ranks(M_fold), ranks(M_fold_pw), ranks(M_shrink)
    rc_naive = r_plug - r_fold          # + = rose under naive fold
    rc_pw = r_plug - r_fold_pw          # + = rose under precision-weighted fold
    rc_shrink = r_plug - r_shrink       # + = rose under EB-shrinkage fold
    cov_corr_naive = spear(np.log(cov_t + 1), rc_naive)
    cov_corr_pw = spear(np.log(cov_t + 1), rc_pw)
    cov_corr_shrink = spear(np.log(cov_t + 1), rc_shrink)

    def risers_of(rc, rfold, key):
        top = np.argsort(-rc)[:15]
        return top, [{"target": str(uniq_t[i]), "rank_plug": int(r_plug[i]) + 1,
                      key: int(rfold[i]) + 1, "rose": int(rc[i]), "total_cells": int(cov_t[i]),
                      "noise_share": round(float(noise_share[i]), 3)} for i in top]
    top_naive, risers_naive = risers_of(rc_naive, r_fold, "rank_fold_naive")
    top_pw, risers_pw = risers_of(rc_pw, r_fold_pw, "rank_fold_pw")
    top_shrink, risers_shrink = risers_of(rc_shrink, r_shrink, "rank_fold_shrink")

    out = {
        "issue": 20, "step": "a-subset", "n_genes_subset": len(gsub), "n_target": n_target,
        "seed": SEED, "median_total_cells_per_target": int(np.median(cov_t)),
        "naive_fold": {
            "spearman_vs_plug": round(spear(r_plug, r_fold), 4),
            "top100_overlap": round(len(topK(M_plug) & topK(M_fold)) / 100, 4),
            "coverage_vs_rankchange_corr": round(cov_corr_naive, 4),
            "mean_noise_share_top_risers": round(float(noise_share[top_naive].mean()), 3),
            "top_risers": risers_naive},
        "precision_weighted_fold": {
            "spearman_vs_plug": round(spear(r_plug, r_fold_pw), 4),
            "top100_overlap": round(len(topK(M_plug) & topK(M_fold_pw)) / 100, 4),
            "coverage_vs_rankchange_corr": round(cov_corr_pw, 4),
            "mean_noise_share_top_risers": round(float(noise_share[top_pw].mean()), 3),
            "top_risers": risers_pw},
        "eb_shrinkage_fold": {
            "spearman_vs_plug": round(spear(r_plug, r_shrink), 4),
            "top100_overlap": round(len(topK(M_plug) & topK(M_shrink)) / 100, 4),
            "coverage_vs_rankchange_corr": round(cov_corr_shrink, 4),
            "mean_noise_share_top_risers": round(float(noise_share[top_shrink].mean()), 3),
            "top_risers": risers_shrink},
        "interpretation": "if precision-weighting collapses coverage_vs_rankchange_corr toward 0 and "
        "the naive risers' noise_share is high, the naive fold's lift of sparse targets was low-count "
        "noise inflation, not de-attenuation of real signal",
    }
    dst = os.path.join(HERE, "..", "results", "synthetic_recovery", "fold_realdata_subset.json")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w") as fo:
        json.dump(out, fo, indent=2)
    log("DONE")
    print(f"\nnaive fold : spearman={spear(r_plug, r_fold):.3f}  cov~Δrank corr={cov_corr_naive:+.3f}  "
          f"risers' mean noise_share={noise_share[top_naive].mean():.2f}")
    print(f"prec-wtd   : spearman={spear(r_plug, r_fold_pw):.3f}  cov~Δrank corr={cov_corr_pw:+.3f}  "
          f"risers' mean noise_share={noise_share[top_pw].mean():.2f}")
    print(f"EB-shrink  : spearman={spear(r_plug, r_shrink):.3f}  cov~Δrank corr={cov_corr_shrink:+.3f}  "
          f"risers' mean noise_share={noise_share[top_shrink].mean():.2f}")
    print("  (does EB shrinkage recover a coverage advantage that precision-weighting missed?)")


if __name__ == "__main__":
    main()
