#!/usr/bin/env python3
"""d_study.py  —  issue #12: the D-study generalizability coefficient (概推度), computed directly
from the variance components. No re-fit, no leave-one-out.

Per gene, from {s2_T, s2_TG, s2_TD, s2_res}:
  R_guide   = s2_T / (s2_T + s2_TG)                       single-guide generalizability
  R_donor   = s2_T / (s2_T + s2_TD)                       single-donor generalizability
  Erho2     = s2_T / (s2_T + s2_TG/n_g + s2_TD/n_d + s2_res/(n_g*n_d))   design-level (n_g=2, n_d=4)
Reported as a profile (per-gene distribution). NOTE: s2_TD has 3 df (4 donors) — the donor coefficient
is intrinsically noisy (design.md §5.2); read the profile, not any single gene's point value.
"""
import csv, os, numpy as np, json
here = os.path.dirname(os.path.abspath(__file__))
N_G, N_D = 2, 4

def d_study(path, keys):
    rows = list(csv.DictReader(open(path)))
    out = []
    for r in rows:
        try:
            sT, sTG, sTD, sRes = (float(r[keys[k]]) for k in ("T", "TG", "TD", "res"))
        except (ValueError, KeyError):
            continue
        if sT + sTG + sTD + sRes <= 0:
            continue
        Rg = sT / (sT + sTG) if (sT + sTG) > 0 else np.nan
        Rd = sT / (sT + sTD) if (sT + sTD) > 0 else np.nan
        Er = sT / (sT + sTG / N_G + sTD / N_D + sRes / (N_G * N_D))
        out.append((r["gene"], Rg, Rd, Er, sT))
    return out

def profile(vals, sig_mask=None):
    a = np.array(vals, float); a = a[np.isfinite(a)]
    q = lambda p: round(float(np.quantile(a, p)), 4)
    return {"median": q(.5), "p25": q(.25), "p75": q(.75), "p90": q(.90), "p95": q(.95)}

report = {}
for label, path, keys in [
    ("raw", os.path.join(here, "pwm_components.csv"),
     dict(T="s2_T", TG="s2_TG", TD="s2_TD", res="s2_res")),
    ("me_corrected", os.path.join(here, "pwm_components_meCorrected.csv"),
     dict(T="s2_T", TG="s2_TG", TD="s2_TD", res="s2_res_bio")),
]:
    if not os.path.exists(path):
        continue
    d = d_study(path, keys)
    Rg = [x[1] for x in d]; Rd = [x[2] for x in d]; Er = [x[3] for x in d]; sT = np.array([x[4] for x in d])
    # focus on genes with real target signal (top decile by s2_T) — where generalizability is meaningful
    thr = np.quantile(sT, 0.90)
    sig = [i for i, x in enumerate(d) if x[4] >= thr]
    report[label] = {
        "n_genes": len(d),
        "R_guide_profile": profile(Rg),
        "R_donor_profile": profile(Rd),
        "Erho2_design_profile": profile(Er),
        "on_top_decile_signal_genes": {
            "R_guide_median": round(float(np.nanmedian([Rg[i] for i in sig])), 4),
            "R_donor_median": round(float(np.nanmedian([Rd[i] for i in sig])), 4),
            "Erho2_median": round(float(np.nanmedian([Er[i] for i in sig])), 4)},
    }

report["design"] = {"n_guides": N_G, "n_donors": N_D,
                    "caveat": "s2_TD has 3 df (4 donors); donor coefficient is noisy — read the profile, not point values (design.md §5.2)"}
json.dump(report, open(os.path.join(here, "d_study.json"), "w"), indent=2)

print("D-study generalizability coefficient (概推度) — profile across genes:")
for label in ("raw", "me_corrected"):
    if label not in report: continue
    r = report[label]; t = r["on_top_decile_signal_genes"]
    print(f"\n[{label}]  (median across all {r['n_genes']} genes | median on top-decile signal genes)")
    print(f"  R_guide  (single-guide generalizability):  {r['R_guide_profile']['median']:.3f} | signal {t['R_guide_median']:.3f}")
    print(f"  R_donor  (single-donor generalizability):  {r['R_donor_profile']['median']:.3f} | signal {t['R_donor_median']:.3f}")
    print(f"  Erho2    (design-level, n_g=2 n_d=4):       {r['Erho2_design_profile']['median']:.3f} | signal {t['Erho2_median']:.3f}")
print("\nwrote d_study.json")
