#!/usr/bin/env python3
"""d_study_projection_percond.py  —  issue #14-B: per-condition D-study.

For each activation state (Rest / Stim8hr / Stim48hr), using the per-condition me-corrected variance
components (fit_pwm_percond.R; representative = median over the fixed pooled-signal gene set), project

  Erho2(n_g, n_d) = s2_T / (s2_T + s2_TG/n_g + s2_TD/n_d + s2_res/(n_g*n_d))

and answer "add guides or donors?" WITHIN each state. condition is a FIXED facet, so this is a
separate within-level D-study; it reveals whether the reliability bottleneck (guide vs donor) is the
same across activation states or itself context-dependent. Design is n_g=2 guides, n_d=4 donors in
every state (guides/donors are crossed with condition).
"""
import csv, os, numpy as np, json
here = os.path.dirname(os.path.abspath(__file__))
CONDS = ["Rest", "Stim8hr", "Stim48hr"]
rows = list(csv.DictReader(open(os.path.join(here, "pwm_components_percond.csv"))))
gs, ds = [1, 2, 4, 6, 8, 12], [1, 2, 4, 6, 8, 12]

def comps(cond):
    sub = [r for r in rows if r["cond"] == cond]
    def col(k):
        v = []
        for r in sub:
            try: v.append(float(r[k]))
            except (ValueError, KeyError): v.append(np.nan)
        return np.array(v)
    sT, sTG, sTD, sRes = col("s2_T"), col("s2_TG"), col("s2_TD"), col("s2_res_bio")
    tot = sT + sTG + sTD + sRes; ok = np.isfinite(tot) & (tot > 0)
    return tuple(float(np.nanmedian(x[ok])) for x in (sT, sTG, sTD, sRes))

out = {}
for cond in CONDS:
    cT, cTG, cTD, cRes = comps(cond)
    E = lambda ng, nd: cT / (cT + cTG / ng + cTD / nd + cRes / (ng * nd))
    base = E(2, 4); gg = E(3, 4) - base; gd = E(2, 5) - base
    def n_needed_g(t, nd=4):
        for ng in range(2, 300):
            if E(ng, nd) >= t: return ng
        return None
    def n_needed_d(t, ng=2):
        for nd in range(4, 300):
            if E(ng, nd) >= t: return nd
        return None
    out[cond] = {
        "components": {"s2_T": round(cT, 4), "s2_TG": round(cTG, 4), "s2_TD": round(cTD, 4), "s2_res": round(cRes, 4)},
        "current_Erho2": round(base, 3),
        "error_terms_at_current": {"guide s2_TG/2": round(cTG / 2, 4), "donor s2_TD/4": round(cTD / 4, 4)},
        "marginal_gain": {"add_1_guide (2->3)": round(gg, 4), "add_1_donor (4->5)": round(gd, 4),
                          "verdict": "add guides" if gg > gd else "add donors"},
        "to_reach_Erho2_0.7": {"guides_needed": n_needed_g(0.7), "donors_needed": n_needed_d(0.7)},
        "surface": {f"n_g={g}": {f"n_d={d}": round(E(g, d), 3) for d in ds} for g in gs},
    }
json.dump(out, open(os.path.join(here, "d_study_projection_percond.json"), "w"), indent=2)

print("per-condition D-study (representative signal-gene components; current design n_g=2, n_d=4):\n")
print(f"  {'state':9} {'Erho2':>6}  {'guide-err':>9} {'donor-err':>9}  verdict     (+guide vs +donor)")
for cond in CONDS:
    o = out[cond]; g = o["error_terms_at_current"]["guide s2_TG/2"]; d = o["error_terms_at_current"]["donor s2_TD/4"]
    m = o["marginal_gain"]
    print(f"  {cond:9} {o['current_Erho2']:>6.3f}  {g:>9.4f} {d:>9.4f}  {m['verdict']:11} "
          f"(+{m['add_1_guide (2->3)']:.4f} vs +{m['add_1_donor (4->5)']:.4f})")
print("\nErho2 surface per state (rows n_g, cols n_d):")
for cond in CONDS:
    print(f"  [{cond}]")
    print("          " + "  ".join(f"n_d={d:<3}" for d in ds))
    for g in gs:
        print(f"    n_g={g:<3} " + "  ".join(f"{out[cond]['surface'][f'n_g={g}'][f'n_d={d}']:.3f}" for d in ds))
print("\nwrote d_study_projection_percond.json")
