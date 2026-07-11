#!/usr/bin/env python3
"""me_removal.py  —  issue #11 refinement: measurement-error removal via the NTC negative control.

The REML residual sigma2_res = sigma2_bio + measurement error. NTC guides carry NO perturbation, so
the variance of the NTC-relative effect AMONG NTC CELLS is a direct, per-gene estimate of the
measurement-error floor (it is stratum-centered by construction, so it is pure within-NTC noise).

Per gene:  sigma2_me = Var(effect | NTC cells)
           sigma2_res_bio = max(0, sigma2_res - sigma2_me)   (boundary-aware)
           corrected shares = {T, TG, TD, res_bio} / sum

This deflates the residual by its measurement-noise part, so the target-signal share rises to its
me-corrected value. No re-fit needed. Writes pwm_components_meCorrected.csv + pwm_summary_meCorrected.json.
"""
import numpy as np, h5py, os, csv, json
here = os.path.dirname(os.path.abspath(__file__))
meta = np.load(os.path.join(here, "meta.npy"), allow_pickle=True).item()
n_obs, n_gene = meta["n_obs"], meta["n_gene"]
eff = np.memmap(os.path.join(here, "effect.f32"), dtype="float32", mode="r", shape=(n_gene, n_obs))

f = h5py.File(os.path.join(here, "..", "..", "data", "raw", "GWCD4i.pseudobulk_merged.h5ad"), "r"); obs = f["obs"]
gt = obs["guide_type"]; cats = [x.decode() for x in gt["categories"][:]]
ntc = np.array([cats[i] == "non-targeting" for i in gt["codes"][:]]); f.close()
ntc_idx = np.where(ntc)[0]
print(f"NTC cells for me estimate: {len(ntc_idx)}")

comp = list(csv.DictReader(open(os.path.join(here, "pwm_components.csv"))))
out_rows = []
me_vals, dres = [], []
for i, r in enumerate(comp):
    if r["s2_res"] in ("NA", ""):
        out_rows.append({**r}); continue
    s2 = {k: float(r[f"s2_{k}"]) for k in ("T", "TG", "TD", "res")}
    s2_me = float(np.var(eff[i][ntc_idx]))                      # measurement-error floor (NTC noise)
    res_bio = max(0.0, s2["res"] - s2_me)
    tot = s2["T"] + s2["TG"] + s2["TD"] + res_bio
    sh = {k: (v / tot if tot > 0 else 0.0) for k, v in
          dict(T=s2["T"], TG=s2["TG"], TD=s2["TD"], res=res_bio).items()}
    me_vals.append(s2_me); dres.append(s2["res"] - res_bio)
    out_rows.append({"gene": r["gene"], "s2_T": s2["T"], "s2_TG": s2["TG"], "s2_TD": s2["TD"],
                     "s2_res_raw": s2["res"], "s2_me": round(s2_me, 6), "s2_res_bio": round(res_bio, 6),
                     "share_T": round(sh["T"], 5), "share_TG": round(sh["TG"], 5),
                     "share_TD": round(sh["TD"], 5), "share_res": round(sh["res"], 5)})

# write corrected components
with open(os.path.join(here, "pwm_components_meCorrected.csv"), "w", newline="") as fo:
    w = csv.DictWriter(fo, fieldnames=list(out_rows[0].keys())); w.writeheader(); w.writerows(out_rows)

valid = [r for r in out_rows if "share_T" in r]
sT = np.array([r["share_T"] for r in valid]); sTraw = np.array([float(comp[i]["share_T"])
      for i, r in enumerate(comp) if comp[i]["share_T"] not in ("NA", "")])
def med(x): return round(float(np.median(x)), 4)
summ = {"method": "me-removal via NTC negative-control variance",
        "n_genes": len(valid),
        "median_s2_me": med(me_vals), "median_residual_removed": med(dres),
        "median_share_T_raw": med(sTraw), "median_share_T_meCorrected": med(sT),
        "genes_share_T_gt_0.10_raw": int((sTraw > 0.10).sum()),
        "genes_share_T_gt_0.10_meCorrected": int((sT > 0.10).sum()),
        "genes_share_T_gt_0.30_meCorrected": int((sT > 0.30).sum()),
        "note": "residual deflated by per-gene NTC measurement-error floor; target ranking preserved, absolute signal share rises"}
json.dump(summ, open(os.path.join(here, "pwm_summary_meCorrected.json"), "w"), indent=2)
print("me-removal (NTC-based):")
print(f"  median share_T: raw={summ['median_share_T_raw']} -> me-corrected={summ['median_share_T_meCorrected']}")
print(f"  genes share_T>0.10: raw={summ['genes_share_T_gt_0.10_raw']} -> meCorrected={summ['genes_share_T_gt_0.10_meCorrected']}")
print(f"  genes share_T>0.30 (meCorrected): {summ['genes_share_T_gt_0.30_meCorrected']}")
print("wrote pwm_components_meCorrected.csv + pwm_summary_meCorrected.json")
