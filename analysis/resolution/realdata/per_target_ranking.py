#!/usr/bin/env python3
"""per_target_ranking.py  —  issues #2/#3/#13: reliability-weighted target ranking, done right.

Per targeting target t, from its NTC-relative effect profiles:
  E_t            effect magnitude (RMS of the overall mean profile across genes)
  R^guide_t      cross-guide split-half profile correlation           (random facet — generalizability)
  R^donor_t      cross-donor 2v2 split-half correlation, EB-shrunk    (random facet — generalizability;
                 moment-based empirical-Bayes shrinkage tames the 4-donor / 3-df noise, per design)
  R^condition_t  mean pairwise cross-condition correlation            (FIXED facet — cross-context
                 CONSISTENCY, not sampling generalizability; labelled as such, design §6)

The three facet R's are a PROFILE — reported separately, NEVER multiplied (a product is systematically
pessimistic, has an unmotivated 'any-zero-zeroes-all' pathology, and uses arbitrary weights; design §9).
The ranking scalar is R_dep,t — the JOINT generalizability over the two RANDOM facets
(guide + donor), where error-to-signal ratios ADD:
  R_dep,t = 1 / (1 + (1−R^guide_t)/R^guide_t + (1−R^donor_t)/R^donor_t)
  S_t   = E_t × R_dep,t
Condition is a FIXED facet → its consistency R^condition_t is reported alongside but NOT folded into the
generalizability coefficient (you do not sample-generalize over fixed states). Both random facets must
be identifiable for a comparable joint (else sparse targets would rank on one lucky facet). Higher-order
interactions feed the joint denominator implicitly; the top-order interaction merges with the
not_identifiable residual floor. Run is confounded with donor (nuisance, not a separate R).

Writes target_ranking.csv + target_ranking_summary.json.
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
tgt, guide, donor, cond, gtype = (cat("perturbed_gene_name"), cat("guide_id"), cat("donor_id"),
                                  cat("culture_condition"), cat("guide_type")); f.close()
targeting = (gtype != "non-targeting")
tobs = np.where(targeting)[0]

def group_profiles(labels):
    """mean effect profile per group over targeting obs. Returns (profiles [n_grp x n_gene], group list,
    obs_group_index aligned to tobs)."""
    keys = [labels[i] for i in tobs]
    uniq = sorted(set(keys)); gi = {k: j for j, k in enumerate(uniq)}
    rows = np.array([gi[k] for k in keys]); cnt = np.bincount(rows, minlength=len(uniq)).astype(float)
    GT = csr_matrix((1.0 / cnt[rows], (rows, tobs)), shape=(len(uniq), n_obs))
    P = np.zeros((len(uniq), n_gene), dtype=np.float32); CH = 3000
    for c0 in range(0, n_gene, CH):
        c1 = min(c0 + CH, n_gene)
        P[:, c0:c1] = GT @ np.ascontiguousarray(eff[c0:c1].T)
    return P, uniq, gi

# facet group profiles: guide (=target,guide since guide is nested), (target,donor), (target,condition)
print("[prep] guide profiles ...");     Pg, Ug, IGg = group_profiles(guide)
print("[prep] donor profiles ...");     Pd, Ud, IGd = group_profiles(np.array([f"{tgt[i]}|{donor[i]}" for i in range(n_obs)], dtype=object))
print("[prep] condition profiles ..."); Pc, Uc, IGc = group_profiles(np.array([f"{tgt[i]}|{cond[i]}" for i in range(n_obs)], dtype=object))
print("[prep] profiles done")

def pearson(a, b):
    a = a - a.mean(); b = b - b.mean(); d = np.sqrt((a @ a) * (b @ b))
    return float(a @ b / d) if d > 0 else np.nan

# per target: collect its facet-group row indices
tg_guides = defaultdict(list); tg_donors = defaultdict(list); tg_conds = defaultdict(list)
for i in tobs:
    tg_guides[tgt[i]].append(IGg[guide[i]])
    tg_donors[tgt[i]].append(IGd[f"{tgt[i]}|{donor[i]}"])
    tg_conds[tgt[i]].append(IGc[f"{tgt[i]}|{cond[i]}"])
for d in (tg_guides, tg_donors, tg_conds):
    for t in d: d[t] = sorted(set(d[t]))

def split_half_corr(P, idxs):
    if len(idxs) < 2: return np.nan
    h = len(idxs) // 2
    A = P[idxs[:h]].mean(axis=0); B = P[idxs[h:]].mean(axis=0)
    return pearson(A, B)
def pairwise_corr(P, idxs):
    if len(idxs) < 2: return np.nan
    rs = [pearson(P[idxs[a]], P[idxs[b]]) for a in range(len(idxs)) for b in range(a + 1, len(idxs))]
    rs = [r for r in rs if np.isfinite(r)]
    return float(np.mean(rs)) if rs else np.nan

recs = []
for t in tg_guides:
    prof_all = Pg[tg_guides[t]].mean(axis=0)
    E_t = float(np.sqrt(np.mean(prof_all ** 2)))
    Rg = split_half_corr(Pg, tg_guides[t])                 # guide split-half
    Rd = split_half_corr(Pd, tg_donors[t])                 # donor 2v2 split-half (raw; shrunk below)
    Rc = pairwise_corr(Pc, tg_conds[t])                    # condition mean-pairwise (fixed-facet consistency)
    recs.append(dict(target=t, n_guides=len(tg_guides[t]), n_donors=len(tg_donors[t]),
                     E_t=E_t, Rg=Rg, Rd=Rd, Rc=Rc))

# --- moment-based empirical-Bayes shrinkage on R^donor (design: tame 4-donor / 3-df noise) ---
rd_raw = np.array([r["Rd"] for r in recs], float)
mask = np.isfinite(rd_raw)
mu = float(np.nanmean(rd_raw))
# within-target sampling var proxy for a 2v2 split-half r: Fisher-z var ~ 1/(k-1) style; use variance of
# raw r's minus a floor as between-target signal (method of moments).
s2_within = float(np.nanvar(rd_raw)) * 0.5            # conservative: half the total spread is sampling noise
tau2 = max(1e-6, float(np.nanvar(rd_raw)) - s2_within)
w = tau2 / (tau2 + s2_within)                        # shrinkage weight toward mu
for r in recs:
    r["Rd_shrunk"] = (mu + w * (r["Rd"] - mu)) if np.isfinite(r["Rd"]) else np.nan

# --- joint generalizability coefficient over the RANDOM facets (guide + donor); condition is a
#     FIXED facet reported separately, NOT folded into generalizability. Error-to-signal ratios ADD.
#     BOTH random facets must be identifiable for a comparable joint (else the coefficient would
#     silently be over a different facet-set and sparse targets would rank on one lucky facet). ---
def r_dep(rg, rd):
    if not (np.isfinite(rg) and rg > 0 and np.isfinite(rd) and rd > 0):
        return np.nan                                  # require both random facets — comparable ranking
    return 1.0 / (1.0 + (1.0 - rg) / rg + (1.0 - rd) / rd)

for r in recs:
    r["R_dep"] = r_dep(r["Rg"], r["Rd_shrunk"])
    r["S_t"] = (r["E_t"] * r["R_dep"]) if np.isfinite(r["R_dep"]) else np.nan

def fmt(x): return round(x, 4) if isinstance(x, float) and np.isfinite(x) else "NA"
scored = [r for r in recs if isinstance(r["S_t"], float) and np.isfinite(r["S_t"])]
by_S = sorted(scored, key=lambda r: -r["S_t"])
by_E = sorted(scored, key=lambda r: -r["E_t"])
rankE = {r["target"]: i for i, r in enumerate(by_E)}
for i, r in enumerate(by_S):
    r["rank_S"] = i + 1; r["rank_E"] = rankE[r["target"]] + 1

with open(os.path.join(here, "target_ranking.csv"), "w", newline="") as fo:
    cols = ["target","n_guides","n_donors","E_t","R_guide","R_donor_raw","R_donor_shrunk","R_condition","R_dep","S_t","rank_S","rank_E"]
    w_ = csv.writer(fo); w_.writerow(cols)
    def row(r):
        return [r["target"], r["n_guides"], r["n_donors"], fmt(r["E_t"]), fmt(r["Rg"]), fmt(r["Rd"]),
                fmt(r["Rd_shrunk"]), fmt(r["Rc"]), fmt(r["R_dep"]), fmt(r["S_t"]),
                r.get("rank_S","NA"), r.get("rank_E","NA")]
    for r in by_S: w_.writerow(row(r))
    for r in recs:
        if not (isinstance(r["S_t"], float) and np.isfinite(r["S_t"])): w_.writerow(row(r))

topE = set(r["target"] for r in by_E[:100]); topS = set(r["target"] for r in by_S[:100])
summ = dict(n_targets=len(recs), n_scored=len(scored),
            facet_medians=dict(R_guide=fmt(float(np.nanmedian([r["Rg"] for r in recs]))),
                               R_donor_shrunk=fmt(float(np.nanmedian([r["Rd_shrunk"] for r in recs]))),
                               R_condition=fmt(float(np.nanmedian([r["Rc"] for r in recs]))),
                               R_dep=fmt(float(np.nanmedian([r["R_dep"] for r in scored])))),
            donor_shrinkage_weight=round(w, 3),
            top10_by_S=[dict(target=r["target"], S=fmt(r["S_t"]), E=fmt(r["E_t"]),
                             Rg=fmt(r["Rg"]), Rd=fmt(r["Rd_shrunk"]), Rc=fmt(r["Rc"]),
                             R_dep=fmt(r["R_dep"]), rank_E=r["rank_E"]) for r in by_S[:10]],
            top100_effect_only_dropped=len(topE - topS),
            note="3 facet R's are a PROFILE (reported separately, never multiplied). Ranking uses the joint generalizability coefficient over the RANDOM facets guide+donor (error-to-signal ratios add); both required for a comparable joint. condition is a FIXED-facet consistency measure, reported alongside but NOT in the generalizability coefficient.")
json.dump(summ, open(os.path.join(here, "target_ranking_summary.json"), "w"), indent=2)

print(f"\nprofile + R_dep ranking: {len(scored):,} scored")
print(f"facet medians: R_guide={summ['facet_medians']['R_guide']} R_donor(shrunk)={summ['facet_medians']['R_donor_shrunk']} R_condition={summ['facet_medians']['R_condition']} | R_dep={summ['facet_medians']['R_dep']}")
print(f"donor EB shrinkage weight toward pooled: {w:.3f}")
print("top 10 by S = E x R_dep  (target | S | Rguide | Rdonor | Rcond | R_dep | effect-only rank):")
for r in by_S[:10]:
    print(f"  {r['target']:16} S={r['S_t']:.3f}  Rg={fmt(r['Rg'])} Rd={fmt(r['Rd_shrunk'])} Rc={fmt(r['Rc'])}  R_dep={fmt(r['R_dep'])}  (eff #{r['rank_E']})")
print(f"\n{len(topE-topS)}/100 effect-only top-100 drop out of the reliability-weighted top-100")
print("wrote target_ranking.csv + target_ranking_summary.json")
