#!/usr/bin/env python3
"""per_target_ranking.py  —  issues #2/#3: the reliability-weighted target ranking (project headline).

For each targeting perturbation target t, from its NTC-relative effect profiles:
  E_t = magnitude of its overall mean effect profile (RMS across genes) — how strongly it perturbs
  R_t = cross-guide split-half reproducibility of the effect profile (Pearson r) — how dependable
  S_t = E_t * max(0, R_t) — reliability-weighted score

Targets with <2 guides get R_t = not_identifiable (fail-closed; no reproducibility to measure).
Ranks by S_t and contrasts with an effect-only ranking (by E_t) — the difference is the point:
a strong-but-guide-unreliable hit drops; a reproducible one rises.

Writes target_ranking.csv (all targets) + target_ranking_summary.json.
"""
import numpy as np, h5py, os, csv, json
from collections import defaultdict
from scipy.sparse import csr_matrix
here = os.path.dirname(os.path.abspath(__file__))
meta = np.load(os.path.join(here, "meta.npy"), allow_pickle=True).item()
n_gene, n_obs = meta["n_gene"], meta["n_obs"]
eff = np.memmap(os.path.join(here, "effect.f32"), dtype="float32", mode="r", shape=(n_gene, n_obs))

f = h5py.File(os.path.join(here, "..", "..", "data", "raw", "GWCD4i.pseudobulk_merged.h5ad"), "r"); obs = f["obs"]
def cat(c):
    g = obs[c]; cats = [x.decode() if isinstance(x, bytes) else str(x) for x in g["categories"][:]]
    return np.array([cats[i] if i >= 0 else "" for i in g["codes"][:]], dtype=object)
tgt, guide, gtype = cat("perturbed_gene_name"), cat("guide_id"), cat("guide_type"); f.close()
targeting = (gtype != "non-targeting")

# targeting guides -> integer index; per-guide obs
tgt_obs = np.where(targeting)[0]
guides = sorted(set(guide[i] for i in tgt_obs))
gidx = {g: k for k, g in enumerate(guides)}
n_guides = len(guides)
rows = np.array([gidx[guide[i]] for i in tgt_obs]); cols = tgt_obs
counts = np.bincount(rows, minlength=n_guides).astype(float)
# G_norm.T : (n_guides x n_obs), each guide-row averages its obs
GT = csr_matrix((1.0 / counts[rows], (rows, cols)), shape=(n_guides, n_obs))
print(f"[prep] {n_guides} targeting guides; computing per-guide mean profiles (gene-chunked matmul)")

# per-guide mean profile matrix: profiles (n_guides x n_gene)
profiles = np.zeros((n_guides, n_gene), dtype=np.float32)
CH = 2000
for c0 in range(0, n_gene, CH):
    c1 = min(c0 + CH, n_gene)
    Dt = np.ascontiguousarray(eff[c0:c1].T)          # (n_obs x chunk)
    profiles[:, c0:c1] = GT @ Dt                     # (n_guides x chunk)
print("[prep] per-guide profiles done")

# per target: guides, split-half R_t, magnitude E_t
tg = defaultdict(list)
for i in tgt_obs:
    g = gidx[guide[i]]
    if g not in tg[tgt[i]]:
        tg[tgt[i]].append(g)

def pearson(a, b):
    a = a - a.mean(); b = b - b.mean()
    d = np.sqrt((a @ a) * (b @ b))
    return float(a @ b / d) if d > 0 else np.nan

recs = []
for t, gl in tg.items():
    prof_all = profiles[gl].mean(axis=0)              # target overall mean profile
    E_t = float(np.sqrt(np.mean(prof_all ** 2)))      # RMS magnitude
    if len(gl) >= 2:
        h = len(gl) // 2
        A = profiles[gl[:h]].mean(axis=0); B = profiles[gl[h:]].mean(axis=0)
        R_t = pearson(A, B)
        r_status = "ok"
    else:
        R_t = np.nan; r_status = "not_identifiable"
    S_t = E_t * max(0.0, R_t) if np.isfinite(R_t) else np.nan
    recs.append(dict(target=t, n_guides=len(gl), E_t=round(E_t, 5),
                     R_t=(round(R_t, 4) if np.isfinite(R_t) else "NA"), R_status=r_status,
                     S_t=(round(S_t, 5) if np.isfinite(S_t) else "NA")))

# rankings
scored = [r for r in recs if r["S_t"] != "NA"]
by_S = sorted(scored, key=lambda r: -r["S_t"])
by_E = sorted(scored, key=lambda r: -r["E_t"])
rankE = {r["target"]: i for i, r in enumerate(by_E)}
for i, r in enumerate(by_S):
    r["rank_S"] = i + 1; r["rank_E"] = rankE[r["target"]] + 1; r["rank_shift"] = r["rank_E"] - r["rank_S"]

with open(os.path.join(here, "target_ranking.csv"), "w", newline="") as fo:
    w = csv.DictWriter(fo, fieldnames=["target","n_guides","E_t","R_t","R_status","S_t","rank_S","rank_E","rank_shift"])
    w.writeheader()
    for r in by_S: w.writerow(r)
    for r in recs:
        if r["S_t"] == "NA": r.update(rank_S="NA", rank_E="NA", rank_shift="NA"); w.writerow(r)

# how much does reliability-weighting change the effect-only top list?
topE = set(r["target"] for r in by_E[:100])
topS = set(r["target"] for r in by_S[:100])
dropped = topE - topS   # strong effect but drop out when reliability-weighted
summ = dict(n_targets=len(recs), n_scored=len(scored),
            n_not_identifiable=sum(1 for r in recs if r["R_status"] == "not_identifiable"),
            top10_by_S=[dict(target=r["target"], S_t=r["S_t"], E_t=r["E_t"], R_t=r["R_t"], rank_E=r["rank_E"]) for r in by_S[:10]],
            top100_effect_only_dropped_by_reliability=len(dropped),
            examples_dropped=sorted(dropped)[:8])
json.dump(summ, open(os.path.join(here, "target_ranking_summary.json"), "w"), indent=2)

print(f"\nreliability-weighted target ranking: {len(scored):,} scored, {summ['n_not_identifiable']} not_identifiable")
print("top 10 by S_t = E_t x R_t (target | S | E | R | effect-only rank):")
for r in by_S[:10]:
    print(f"  {r['target']:18} S={r['S_t']:.3f}  E={r['E_t']:.3f}  R={r['R_t']}  (effect-only rank #{r['rank_E']})")
print(f"\n{len(dropped)}/100 targets in the effect-only top-100 DROP OUT of the reliability-weighted top-100")
print(f"  -> reliability weighting changes {len(dropped)}% of the top list (the project's whole point)")
print("wrote target_ranking.csv + target_ranking_summary.json")
