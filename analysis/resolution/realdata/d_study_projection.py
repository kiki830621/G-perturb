#!/usr/bin/env python3
"""d_study_projection.py  —  issue #12: project Erho2(n_guide, n_donor) to answer "add guides or donors?"

Erho2(n_g, n_d) = s2_T / (s2_T + s2_TG/n_g + s2_TD/n_d + s2_res/(n_g*n_d))

Uses the me-corrected median variance components on the top-decile signal genes (a representative
reliable-target gene). Reports the surface + the marginal gain of +1 guide vs +1 donor at the current
design (n_g=2, n_d=4). The bottleneck facet is the one whose error term s2_facet/n_facet is largest.
"""
import csv, os, numpy as np, json
here = os.path.dirname(os.path.abspath(__file__))

rows = list(csv.DictReader(open(os.path.join(here, "pwm_components_meCorrected.csv"))))
def col(k):
    v = []
    for r in rows:
        try: v.append(float(r[k]))
        except (ValueError, KeyError): v.append(np.nan)
    return np.array(v)
sT, sTG, sTD, sRes = col("s2_T"), col("s2_TG"), col("s2_TD"), col("s2_res_bio")
tot = sT + sTG + sTD + sRes
ok = np.isfinite(tot) & (tot > 0)
# top-decile signal genes (where generalizability is meaningful)
thr = np.nanquantile(sT[ok], 0.90)
sig = ok & (sT >= thr)
# representative components = median over signal genes
cT, cTG, cTD, cRes = (float(np.nanmedian(x[sig])) for x in (sT, sTG, sTD, sRes))
print(f"representative signal-gene components (me-corrected median): "
      f"s2_T={cT:.4f} s2_TG={cTG:.4f} s2_TD={cTD:.4f} s2_res={cRes:.4f}")

def Erho2(ng, nd):
    return cT / (cT + cTG/ng + cTD/nd + cRes/(ng*nd))

# surface over a grid
gs = [1, 2, 4, 6, 8, 12]
ds = [1, 2, 4, 6, 8, 12]
surface = {f"n_g={g}": {f"n_d={d}": round(Erho2(g, d), 3) for d in ds} for g in gs}

# marginal gain at current design (n_g=2, n_d=4)
base = Erho2(2, 4)
gain_guide = Erho2(3, 4) - base       # +1 guide
gain_donor = Erho2(2, 5) - base       # +1 donor
# to reach a target Erho2, how many of each (holding the other at current)?
def n_needed_guides(target, nd=4):
    for ng in range(2, 200):
        if Erho2(ng, nd) >= target: return ng
    return None
def n_needed_donors(target, ng=2):
    for nd in range(4, 200):
        if Erho2(ng, nd) >= target: return nd
    return None

out = {
    "representative_components": {"s2_T": round(cT,4), "s2_TG": round(cTG,4), "s2_TD": round(cTD,4), "s2_res": round(cRes,4)},
    "current_design": {"n_g": 2, "n_d": 4, "Erho2": round(base, 3)},
    "error_terms_at_current": {"guide s2_TG/n_g": round(cTG/2, 4), "donor s2_TD/n_d": round(cTD/4, 4),
                               "residual s2_res/(n_g n_d)": round(cRes/8, 4)},
    "marginal_gain": {"add_1_guide (2->3)": round(gain_guide, 4), "add_1_donor (4->5)": round(gain_donor, 4),
                      "verdict": "add guides" if gain_guide > gain_donor else "add donors"},
    "to_reach_Erho2_0.7": {"guides_needed": n_needed_guides(0.7), "donors_needed": n_needed_donors(0.7)},
    "surface": surface,
}
json.dump(out, open(os.path.join(here, "d_study_projection.json"), "w"), indent=2)

print(f"\ncurrent design (n_g=2, n_d=4): Erho2 = {base:.3f}")
print(f"error terms:  guide s2_TG/2 = {cTG/2:.4f}   donor s2_TD/4 = {cTD/4:.4f}   (bigger = bottleneck)")
print(f"\nmarginal gain:  +1 guide (2->3) = +{gain_guide:.4f}   |   +1 donor (4->5) = +{gain_donor:.4f}")
print(f"  -> VERDICT: {out['marginal_gain']['verdict']}")
print(f"\nto reach Erho2=0.70:  {out['to_reach_Erho2_0.7']['guides_needed']} guides (n_d=4) "
      f"OR {out['to_reach_Erho2_0.7']['donors_needed']} donors (n_g=2)")
print("\nErho2 surface (rows n_g, cols n_d):")
print("        " + "  ".join(f"n_d={d:<3}" for d in ds))
for g in gs:
    print(f"  n_g={g:<3} " + "  ".join(f"{Erho2(g,d):.3f}" for d in ds))
print("\nwrote d_study_projection.json")
