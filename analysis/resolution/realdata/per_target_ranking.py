#!/usr/bin/env python3
"""per_target_ranking.py  —  issues #2/#3/#13/#14: reliability-weighted target ranking, sliced by context.

Per targeting target t, from its NTC-relative effect profiles:
  E_t            effect magnitude (RMS of the overall mean profile across genes)
  R^guide_t      cross-guide split-half profile correlation           (random facet — generalizability)
  R^donor_t      cross-donor 2v2 split-half correlation, EB-shrunk    (random facet — generalizability;
                 moment-based empirical-Bayes shrinkage tames the 4-donor / 3-df noise, per design)
  R^condition_t  mean pairwise cross-condition correlation            (FIXED facet — cross-context
                 CONSISTENCY, not sampling generalizability; overall view only, design §6)

The three facet R's are a PROFILE — reported separately, NEVER multiplied (a product is systematically
pessimistic, has an unmotivated 'any-zero-zeroes-all' pathology, and uses arbitrary weights; design §9).
The ranking scalar is R_dep,t — the JOINT generalizability over the two RANDOM facets (guide + donor),
where error-to-signal ratios ADD:
  R_dep,t = 1 / (1 + (1−R^guide_t)/R^guide_t + (1−R^donor_t)/R^donor_t)
  S_t     = E_t × R_dep,t

#14 — CONTEXT SLICING. condition is a FIXED facet (Rest / Stim8hr / Stim48hr = 3 chosen activation
states, not a random sample), so the textbook G-theory treatment is a SEPARATE analysis within each
level. We compute the whole profile (E_t, R^guide, R^donor, R_dep) for four VIEWS: `overall` +
one per condition. Each condition slice restricts to that condition's obs; EB shrinkage is
re-estimated PER VIEW (per-slice noise differs). Fail-closed: a target x view with < 2 guides or
< 2 donors → R_dep = NaN (not_identifiable). R^condition is defined only on the `overall` view
(a single-condition slice has no cross-condition dimension). Both random facets absorb measurement
error by construction (split-half), so NO me-removal on this path (that is the d_study path).

CONTEXT-SPECIFICITY: per-slice R_dep runs systematically LOWER than overall (each slice averages ~1/3
the cells → noisier profiles), so slices are compared to EACH OTHER, never slice-vs-overall. A target
dependable in one activation state but not another (large across-slice spread) is context-specific-but-
reliable — a real biological signal that pooled ranking and effect size both miss.

Writes: target_ranking.csv (overall headline, backward-compatible) + target_ranking_percond.csv
(long: target x view) + target_context_specificity.csv (classifier) + target_ranking_summary.json.
"""
import numpy as np, h5py, os, csv, json
from collections import defaultdict
from itertools import combinations
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
# per-obs facet labels (guide is nested in target; donor/cond keyed by target)
guide_lab = guide
donor_lab = np.array([f"{tgt[i]}|{donor[i]}" for i in range(n_obs)], dtype=object)
cond_lab  = np.array([f"{tgt[i]}|{cond[i]}"  for i in range(n_obs)], dtype=object)
CONDS = ["Rest", "Stim8hr", "Stim48hr"]

def group_profiles(labels, view_tobs):
    """mean effect profile per group over view_tobs. Returns (profiles [n_grp x n_gene], group->row idx)."""
    keys = [labels[i] for i in view_tobs]
    uniq = sorted(set(keys)); gi = {k: j for j, k in enumerate(uniq)}
    rows = np.array([gi[k] for k in keys]); cnt = np.bincount(rows, minlength=len(uniq)).astype(float)
    GT = csr_matrix((1.0 / cnt[rows], (rows, view_tobs)), shape=(len(uniq), n_obs))
    P = np.zeros((len(uniq), n_gene), dtype=np.float32); CH = 3000
    for c0 in range(0, n_gene, CH):
        c1 = min(c0 + CH, n_gene)
        P[:, c0:c1] = GT @ np.ascontiguousarray(eff[c0:c1].T)
    return P, gi

def pearson(a, b):
    a = a - a.mean(); b = b - b.mean(); d = np.sqrt((a @ a) * (b @ b))
    return float(a @ b / d) if d > 0 else np.nan
def split_half_corr(P, idxs):
    if len(idxs) < 2: return np.nan
    h = len(idxs) // 2
    return pearson(P[idxs[:h]].mean(axis=0), P[idxs[h:]].mean(axis=0))
def avg_split_half_corr(P, idxs):
    # order-independent split-half: average the mean-profile correlation over ALL balanced
    # half-splits of idxs (for 4 donors, the 3 distinct 2v2 splits; for 2 units, the single
    # split). Removes the arbitrariness of one fixed split without changing the estimand.
    n = len(idxs)
    if n < 2: return np.nan
    h = n // 2
    rs, seen = [], set()
    for combo in combinations(range(n), h):
        comp = tuple(sorted(set(range(n)) - set(combo)))
        key = tuple(sorted((tuple(combo), comp)))   # dedup mirror splits (A|B == B|A)
        if key in seen: continue
        seen.add(key)
        a = [idxs[i] for i in combo]; b = [idxs[i] for i in comp]
        r = pearson(P[a].mean(axis=0), P[b].mean(axis=0))
        if np.isfinite(r): rs.append(r)
    return float(np.mean(rs)) if rs else np.nan
def pairwise_corr(P, idxs):
    if len(idxs) < 2: return np.nan
    rs = [pearson(P[idxs[a]], P[idxs[b]]) for a in range(len(idxs)) for b in range(a + 1, len(idxs))]
    rs = [r for r in rs if np.isfinite(r)]
    return float(np.mean(rs)) if rs else np.nan

def r_dep(rg, rd):
    # joint generalizability over the RANDOM facets (guide + donor); BOTH must be identifiable for a
    # comparable joint (else sparse targets rank on one lucky facet). condition is FIXED, excluded.
    if not (np.isfinite(rg) and rg > 0 and np.isfinite(rd) and rd > 0):
        return np.nan
    return 1.0 / (1.0 + (1.0 - rg) / rg + (1.0 - rd) / rd)

def compute_view(view_tobs, label, with_condition):
    """full per-target profile within one view (all targeting obs, or one condition slice)."""
    Pg, IGg = group_profiles(guide_lab, view_tobs)
    Pd, IGd = group_profiles(donor_lab, view_tobs)
    Pc, IGc = group_profiles(cond_lab, view_tobs) if with_condition else (None, None)
    tg_guides, tg_donors, tg_conds = defaultdict(list), defaultdict(list), defaultdict(list)
    for i in view_tobs:
        tg_guides[tgt[i]].append(IGg[guide_lab[i]])
        tg_donors[tgt[i]].append(IGd[donor_lab[i]])
        if with_condition: tg_conds[tgt[i]].append(IGc[cond_lab[i]])
    for dd in (tg_guides, tg_donors, tg_conds):
        for t in dd: dd[t] = sorted(set(dd[t]))
    recs = {}
    for t in tg_guides:
        prof_all = Pg[tg_guides[t]].mean(axis=0)
        recs[t] = dict(target=t, view=label, n_guides=len(tg_guides[t]), n_donors=len(tg_donors[t]),
                       E_t=float(np.sqrt(np.mean(prof_all ** 2))),
                       Rg=split_half_corr(Pg, tg_guides[t]),
                       Rd=avg_split_half_corr(Pd, tg_donors[t]),
                       Rc=(pairwise_corr(Pc, tg_conds[t]) if with_condition else np.nan))
    # per-VIEW moment-based EB shrinkage on R^donor (per-slice noise differs → re-estimate μ, w)
    rd_raw = np.array([r["Rd"] for r in recs.values()], float)
    mu = float(np.nanmean(rd_raw)); tot_var = float(np.nanvar(rd_raw))
    s2_within = tot_var * 0.5; tau2 = max(1e-6, tot_var - s2_within); w = tau2 / (tau2 + s2_within)
    for r in recs.values():
        r["Rd_shrunk"] = (mu + w * (r["Rd"] - mu)) if np.isfinite(r["Rd"]) else np.nan
        r["R_dep"] = r_dep(r["Rg"], r["Rd_shrunk"])
        r["S_t"] = (r["E_t"] * r["R_dep"]) if np.isfinite(r["R_dep"]) else np.nan
    return recs, round(w, 3)

# --- four views: overall + one per condition ---
views = [("overall", np.where(targeting)[0], True)]
for c in CONDS:
    views.append((c, np.where(targeting & (cond == c))[0], False))
all_recs, view_w = {}, {}
for label, vt, wc in views:
    print(f"[view] {label} ({len(vt):,} obs) ...", flush=True)
    all_recs[label], view_w[label] = compute_view(vt, label, wc)
print("[views done]")

def fmt(x): return round(x, 4) if isinstance(x, float) and np.isfinite(x) else "NA"

# === 1) overall headline ranking (backward-compatible target_ranking.csv) ===
ov = all_recs["overall"]
scored = [r for r in ov.values() if isinstance(r["S_t"], float) and np.isfinite(r["S_t"])]
by_S = sorted(scored, key=lambda r: -r["S_t"]); by_E = sorted(scored, key=lambda r: -r["E_t"])
rankE = {r["target"]: i for i, r in enumerate(by_E)}
for i, r in enumerate(by_S):
    r["rank_S"] = i + 1; r["rank_E"] = rankE[r["target"]] + 1
with open(os.path.join(here, "target_ranking.csv"), "w", newline="") as fo:
    w_ = csv.writer(fo)
    w_.writerow(["target","n_guides","n_donors","E_t","R_guide","R_donor_raw","R_donor_shrunk",
                 "R_condition","R_dep","S_t","rank_S","rank_E"])
    def orow(r):
        return [r["target"], r["n_guides"], r["n_donors"], fmt(r["E_t"]), fmt(r["Rg"]), fmt(r["Rd"]),
                fmt(r["Rd_shrunk"]), fmt(r["Rc"]), fmt(r["R_dep"]), fmt(r["S_t"]),
                r.get("rank_S","NA"), r.get("rank_E","NA")]
    for r in by_S: w_.writerow(orow(r))
    for r in ov.values():
        if not (isinstance(r["S_t"], float) and np.isfinite(r["S_t"])): w_.writerow(orow(r))

# === 2) per-condition long table (target x view) ===
with open(os.path.join(here, "target_ranking_percond.csv"), "w", newline="") as fo:
    w_ = csv.writer(fo)
    w_.writerow(["target","view","n_guides","n_donors","E_t","R_guide","R_donor_shrunk","R_dep","S_t"])
    for label, _, _ in views:
        for r in sorted(all_recs[label].values(), key=lambda r: (-(r["S_t"] if np.isfinite(r["S_t"]) else -1))):
            w_.writerow([r["target"], label, r["n_guides"], r["n_donors"], fmt(r["E_t"]),
                         fmt(r["Rg"]), fmt(r["Rd_shrunk"]), fmt(r["R_dep"]), fmt(r["S_t"])])

# === 3) context-specificity classifier (slices compared to EACH OTHER, never to overall) ===
# For each target with >=2 identifiable condition slices: best state, across-slice spread, relative drop.
cs_rows = []
for t in ov:
    slice_rdep = {c: all_recs[c].get(t, {}).get("R_dep", np.nan) for c in CONDS}
    ident = {c: v for c, v in slice_rdep.items() if isinstance(v, float) and np.isfinite(v)}
    rdep_ov = ov[t]["R_dep"]
    if len(ident) >= 2:
        best_state = max(ident, key=ident.get); mx = ident[best_state]; mn = min(ident.values())
        spread = mx - mn                                    # absolute across-slice spread
        rel_drop = spread / mx if mx > 0 else np.nan        # fraction lost from best to weakest state
        # context-specific-but-reliable: dependable in the best state, much weaker in another
        cs_flag = bool(mx >= 0.15 and mn < 0.5 * mx)
    else:
        best_state = (next(iter(ident)) if len(ident) == 1 else "NA")
        mx = ident[best_state] if len(ident) == 1 else np.nan
        mn = np.nan; spread = np.nan; rel_drop = np.nan
        cs_flag = False                                     # <2 identifiable slices → not classifiable
    cs_rows.append(dict(target=t, Rdep_overall=rdep_ov, best_state=best_state, best_Rdep=mx,
                        n_slices_ident=len(ident), cs_spread=spread, cs_rel_drop=rel_drop,
                        cs_flag=cs_flag,
                        **{f"Rdep_{c}": slice_rdep[c] for c in CONDS}))
cs_scored = [r for r in cs_rows if r["cs_flag"]]
cs_scored.sort(key=lambda r: -(r["cs_spread"] if np.isfinite(r["cs_spread"]) else -1))
with open(os.path.join(here, "target_context_specificity.csv"), "w", newline="") as fo:
    cols = ["target","best_state","best_Rdep","cs_spread","cs_rel_drop","cs_flag","n_slices_ident",
            "Rdep_overall","Rdep_Rest","Rdep_Stim8hr","Rdep_Stim48hr"]
    w_ = csv.writer(fo); w_.writerow(cols)
    for r in sorted(cs_rows, key=lambda r: -(r["cs_spread"] if np.isfinite(r["cs_spread"]) else -1)):
        w_.writerow([r["target"], r["best_state"], fmt(r["best_Rdep"]), fmt(r["cs_spread"]),
                     fmt(r["cs_rel_drop"]), r["cs_flag"], r["n_slices_ident"], fmt(r["Rdep_overall"]),
                     fmt(r["Rdep_Rest"]), fmt(r["Rdep_Stim8hr"]), fmt(r["Rdep_Stim48hr"])])

# === 4) summary ===
def med_rdep(label):
    v = [r["R_dep"] for r in all_recs[label].values() if isinstance(r["R_dep"], float) and np.isfinite(r["R_dep"])]
    return fmt(float(np.median(v))) if v else "NA"
def n_scored(label):
    return sum(1 for r in all_recs[label].values() if isinstance(r["S_t"], float) and np.isfinite(r["S_t"]))
best_state_counts = defaultdict(int)
for r in cs_scored: best_state_counts[r["best_state"]] += 1
summ = dict(
    n_targets=len(ov), n_scored_overall=len(scored),
    per_view=dict((label, dict(n_scored=n_scored(label), median_R_dep=med_rdep(label),
                               donor_shrink_w=view_w[label])) for label, _, _ in views),
    overall_top10=[dict(target=r["target"], S=fmt(r["S_t"]), R_dep=fmt(r["R_dep"]),
                        rank_E=r["rank_E"]) for r in by_S[:10]],
    context_specific=dict(
        n_flagged=len(cs_scored),
        best_state_counts=dict(best_state_counts),
        top15=[dict(target=r["target"], best_state=r["best_state"], best_Rdep=fmt(r["best_Rdep"]),
                    cs_spread=fmt(r["cs_spread"]),
                    Rdep_Rest=fmt(r["Rdep_Rest"]), Rdep_Stim8hr=fmt(r["Rdep_Stim8hr"]),
                    Rdep_Stim48hr=fmt(r["Rdep_Stim48hr"])) for r in cs_scored[:15]]),
    note="4 views (overall + Rest/Stim8hr/Stim48hr). condition is a FIXED facet, analysed within-level. "
         "R_dep is joint generalizability over the RANDOM facets guide+donor; both required. Per-slice "
         "R_dep runs lower than overall (fewer cells) so slices are compared to EACH OTHER; a large "
         "across-slice spread = context-specific-but-reliable target (real signal, not noise).")
json.dump(summ, open(os.path.join(here, "target_ranking_summary.json"), "w"), indent=2)

print(f"\noverall headline ranking: {len(scored):,} scored (target_ranking.csv unchanged schema)")
print(f"per-view scored / median R_dep / donor-shrink w:")
for label, _, _ in views:
    print(f"  {label:10} n={n_scored(label):5}  medR_dep={med_rdep(label)}  w={view_w[label]}")
print(f"\ncontext-specific-but-reliable targets flagged: {len(cs_scored)}")
print(f"  best-state distribution: {dict(best_state_counts)}")
print(f"  top 8 by across-slice spread (dependable in one activation state, weak in another):")
for r in cs_scored[:8]:
    print(f"    {r['target']:12} best={r['best_state']:8} R_dep={fmt(r['best_Rdep'])}  "
          f"(Rest={fmt(r['Rdep_Rest'])} 8hr={fmt(r['Rdep_Stim8hr'])} 48hr={fmt(r['Rdep_Stim48hr'])})  "
          f"spread={fmt(r['cs_spread'])}")
print("\nwrote target_ranking.csv + target_ranking_percond.csv + target_context_specificity.csv + summary")
