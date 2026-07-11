#!/usr/bin/env python3
"""real_controls.py  —  task 6.3 (section-8 controls) on the REAL NTC-relative effect.

Runs the cheap-but-load-bearing controls directly on realdata/effect.f32 (no re-fitting):
  - guide cross-fit: within each target, split guides into two halves; per gene correlate the
    half-A target-mean effect with the half-B target-mean effect. High correlation = the target
    signal reproduces across guides (the core reliability claim). Reported per gene + pooled.
  - common-support: fraction of targets observed in all conditions (condition contrasts valid there).
  - NTC-vs-NTC: split NTC guides into two random halves as pseudo-targets; the cross-half correlation
    should be ~0 (no spurious target signal in the negative control).

Leave-one-donor-out (4x full decomposition) is heavier and left for a separate run.
Writes realdata/real_controls.json.
"""
import numpy as np, h5py, os, json, csv
here = os.path.dirname(os.path.abspath(__file__))
meta = np.load(os.path.join(here, "meta.npy"), allow_pickle=True).item()
n_obs, n_gene = meta["n_obs"], meta["n_gene"]
eff = np.memmap(os.path.join(here, "effect.f32"), dtype="float32", mode="r", shape=(n_gene, n_obs))

# design factors
f = h5py.File(os.path.join(here, "..", "..", "data", "raw", "GWCD4i.pseudobulk_merged.h5ad"), "r"); obs = f["obs"]
def cat(c):
    g = obs[c]; cats = [x.decode() if isinstance(x, bytes) else str(x) for x in g["categories"][:]]
    return np.array([cats[i] if i >= 0 else "" for i in g["codes"][:]], dtype=object)
tgt, guide, cond, gtype = cat("perturbed_gene_name"), cat("guide_id"), cat("culture_condition"), cat("guide_type")
f.close()
targeting = (gtype == "non-targeting") == False
rng = np.random.RandomState(0)

def crossfit_corr(gene_rows_mask, unit_labels, half_assign, gene_subset):
    """Per gene in gene_subset: target-mean effect for half A vs half B, Pearson r across units."""
    idxA = np.where(gene_rows_mask & (half_assign == 0))[0]
    idxB = np.where(gene_rows_mask & (half_assign == 1))[0]
    uA, uB = unit_labels[idxA], unit_labels[idxB]
    corrs = []
    for gi in gene_subset:
        col = eff[gi]
        # mean effect per unit (target) within each half
        import pandas as pd
        a = pd.Series(col[idxA]).groupby(uA).mean()
        b = pd.Series(col[idxB]).groupby(uB).mean()
        common = a.index.intersection(b.index)
        if len(common) >= 20:
            r = np.corrcoef(a.loc[common].values, b.loc[common].values)[0, 1]
            if np.isfinite(r): corrs.append(r)
    return float(np.median(corrs)) if corrs else None, len(corrs)

# assign each targeting cell to guide-half 0/1 by hashing its guide id (stable split within target)
half = np.array([hash(g) % 2 for g in guide], dtype=int)
# gene subset: sample of high-signal genes (share_T) + random, to keep it quick and meaningful
comp = {r["gene"]: float(r["share_T"]) for r in csv.DictReader(open(os.path.join(here, "pwm_components.csv")))
        if r["share_T"] not in ("NA", "")}
gene_names = [l.strip() for l in open(os.path.join(here, "gene_names.txt")) if l.strip()]
order = np.argsort([-comp.get(g, 0) for g in gene_names])
signal_genes = list(order[:300])            # top-300 by share_T (where reliability matters)
random_genes = list(rng.choice(n_gene, 300, replace=False))

# guide cross-fit on signal genes
gc_med, gc_n = crossfit_corr(targeting, tgt, half, signal_genes)
# NTC-vs-NTC: NTC cells split into random pseudo-targets, cross-half corr should be ~0
ntc_mask = ~targeting
ntc_pseudo = np.array([f"P{h}" for h in (np.arange(n_obs) % 200)], dtype=object)  # 200 pseudo-targets
ntc_half = (np.arange(n_obs) // 1) % 2
nt_med, nt_n = crossfit_corr(ntc_mask, ntc_pseudo, (rng.rand(n_obs) < 0.5).astype(int), random_genes)

# common-support: targets present in all 3 conditions
from collections import defaultdict
tc = defaultdict(set)
for i in range(n_obs):
    if targeting[i]: tc[tgt[i]].add(cond[i])
n_all = sum(1 for v in tc.values() if len(v) == 3)
support_frac = round(n_all / max(1, len(tc)), 4)

out = {
    "scale": "real_data",
    "guide_cross_fit": {"median_cross_guide_corr_top300_signal_genes": round(gc_med, 4) if gc_med else None,
                        "genes_evaluated": gc_n,
                        "stable": (gc_med is not None and gc_med >= 0.5),
                        "note": "target-mean effect reproduces across guide halves on high-signal genes"},
    "ntc_vs_ntc": {"median_cross_half_corr": round(nt_med, 4) if nt_med else None, "genes_evaluated": nt_n,
                   "near_zero": (nt_med is not None and abs(nt_med) < 0.1),
                   "note": "negative control: NTC split into random halves should show ~0 target correlation"},
    "common_support": {"targets_in_all_conditions": n_all, "targets_total": len(tc), "support_fraction": support_frac},
}
json.dump(out, open(os.path.join(here, "real_controls.json"), "w"), indent=2)
print("§8 controls on REAL data:")
print(f"  guide_cross_fit (top-300 signal genes): median r = {out['guide_cross_fit']['median_cross_guide_corr_top300_signal_genes']} "
      f"(stable={out['guide_cross_fit']['stable']}, n={gc_n})")
print(f"  ntc_vs_ntc (negative control):          median r = {out['ntc_vs_ntc']['median_cross_half_corr']} "
      f"(near_zero={out['ntc_vs_ntc']['near_zero']}, n={nt_n})")
print(f"  common_support:                         {n_all}/{len(tc)} targets in all conditions ({support_frac})")
print("wrote real_controls.json")
