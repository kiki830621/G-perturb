#!/usr/bin/env python3
"""build_manifest.py  —  task 1.2 (spec: "Frozen empirical evidence manifest over the joint pseudobulk").

Reads the JOINT pseudobulk GWCD4i.pseudobulk_merged.h5ad and emits a versioned, checksummed evidence
manifest of the REAL target×guide×donor×condition design: grid, completeness, per-component
identifiability (fail-closed), run×donor separability, replication-floor status, NTC coverage, the
measurement-error (n_cells) distribution, and QC. Marginal by_guide/by_donors are NOT accepted here.

FAIL-CLOSED: absent file → non-zero exit, no fabrication. A component whose facet does not vary within
its parent grouping is recorded `not_identifiable`, never zero-filled or renamed.

Confirmed schema (h5py inspection, 2026-07): target=perturbed_gene_name, guide=guide_id,
donor=donor_id, condition=culture_condition, run=10xrun_id, NTC=guide_type=="non-targeting",
measurement error via n_cells; QC via keep_for_DE.
"""
import argparse, json, hashlib, os, sys
from collections import defaultdict

def die(msg, code=2):
    print(f"[build_manifest] FAIL-CLOSED: {msg}", file=sys.stderr); sys.exit(code)

def read_obs(path, cols):
    import h5py, numpy as np
    if not os.path.exists(path):
        die(f"joint pseudobulk not found at {path}. Run download/fetch_joint_pseudobulk.sh first; "
            f"marginal by_guide/by_donors are NOT acceptable substitutes.")
    out = {}
    with h5py.File(path, "r") as f:
        if "obs" not in f: die("no /obs group; not an AnnData file?")
        obs = f["obs"]
        for key, name in cols.items():
            if name is None: continue
            if name not in obs: die(f".obs column '{name}' missing; pass the right --obs-{key}.")
            node = obs[name]
            if isinstance(node, h5py.Group) and "categories" in node:
                cats = [c.decode() if isinstance(c, bytes) else str(c) for c in node["categories"][:]]
                codes = node["codes"][:]
                out[key] = np.array([cats[i] if i >= 0 else None for i in codes], dtype=object)
            else:
                out[key] = node[:]
    return out

def identifiable_within(anchor_cols, vary_col, rows):
    """Fraction of anchor groups in which `vary_col` takes >=2 values. Identifiable iff > 0; the
    fraction reports the STRENGTH of identification (fail-closed on 0)."""
    seen = defaultdict(set)
    for i in range(len(rows[vary_col])):
        key = tuple(rows[c][i] for c in anchor_cols)
        seen[key].add(rows[vary_col][i])
    counts = [len(v) for v in seen.values()]
    frac = sum(c >= 2 for c in counts) / max(1, len(counts))
    return frac

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--joint", required=True)
    ap.add_argument("--obs-target", default="perturbed_gene_name")
    ap.add_argument("--obs-guide", default="guide_id")
    ap.add_argument("--obs-donor", default="donor_id")
    ap.add_argument("--obs-condition", default="culture_condition")
    ap.add_argument("--obs-run", default="10xrun_id")
    ap.add_argument("--obs-ncells", default="n_cells")
    ap.add_argument("--obs-guidetype", default="guide_type")
    ap.add_argument("--obs-keep", default="keep_for_DE")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results", "evidence.manifest.json"))
    a = ap.parse_args()
    import numpy as np

    r = read_obs(a.joint, dict(target=a.obs_target, guide=a.obs_guide, donor=a.obs_donor,
                               condition=a.obs_condition, run=a.obs_run, n_cells=a.obs_ncells,
                               guide_type=a.obs_guidetype, keep=a.obs_keep))
    N = len(r["target"])
    U = lambda k: sorted(set(r[k]))
    targets, guides, donors, conds, runs = U("target"), U("guide"), U("donor"), U("condition"), U("run")

    # per-component identifiability (fail-closed parent check) with strength fraction
    def gate(frac): return {"status": "empirically_passed" if frac > 0 else "not_identifiable",
                            "fraction_identifiable": round(frac, 4)}
    ident = {
        "T":  {"status": "empirically_passed" if len(targets) >= 2 else "not_identifiable", "fraction_identifiable": 1.0},
        "TG": gate(identifiable_within(["target"], "guide", r)),
        "TD": gate(identifiable_within(["target", "guide"], "donor", r)),
        "TC": gate(identifiable_within(["target", "guide", "donor"], "condition", r)),
    }

    # replication floor: does any (target,guide,donor,condition) spec have >1 row (across runs = lane)?
    spec_rows = defaultdict(int)
    for i in range(N):
        spec_rows[(r["target"][i], r["guide"][i], r["donor"][i], r["condition"][i])] += 1
    max_rep = max(spec_rows.values()) if spec_rows else 0
    floor = "empirically_passed" if max_rep >= 2 else "not_identifiable"

    # run x donor separability: is run aliased within donor (each donor in one run only)?
    run_by_donor = defaultdict(set)
    for i in range(N): run_by_donor[r["donor"][i]].add(r["run"][i])
    donors_single_run = {d: sorted(v) for d, v in run_by_donor.items() if len(v) == 1}
    run_donor_status = "not_identifiable" if all(len(v) <= 1 for v in run_by_donor.values()) else \
                       ("partially_confounded" if donors_single_run else "empirically_passed")

    # measurement error (n_cells) + NTC + QC
    nc = np.asarray(r["n_cells"], dtype=float)
    ntc = np.array([str(x) == "non-targeting" for x in r["guide_type"]])
    keep = np.asarray(r["keep"]).astype(bool)
    poss = len(guides) * len(donors) * len(conds) * len(runs)

    payload = {
        "schema_version": "1.0",
        "joint_source": os.path.basename(a.joint),
        "n_obs": N,
        "grid": {"n_targets": len(targets), "n_guides": len(guides), "n_donors": len(donors),
                 "n_conditions": len(conds), "n_runs": len(runs),
                 "completeness_guide_donor_cond_run": round(N / max(1, poss), 4)},
        "identifiability": ident,
        "replication_floor": {"max_rows_per_spec": int(max_rep), "status": floor,
                              "note": "run does not create identical-spec replicates" if floor == "not_identifiable" else "lane replicate present"},
        "separability_run_donor": {"status": run_donor_status,
                                   "donors_single_run": donors_single_run,
                                   "note": "run partially confounded with donor" if run_donor_status == "partially_confounded" else ""},
        "ntc": {"n_ntc_cells": int(ntc.sum()), "fraction": round(float(ntc.mean()), 4)},
        "measurement_error": {"n_cells_min": float(nc.min()), "n_cells_median": float(np.median(nc)),
                              "n_cells_max": float(nc.max()), "n_singleton_cells": int((nc == 1).sum())},
        "qc": {"keep_for_DE_true": int(keep.sum()), "fraction": round(float(keep.mean()), 4)},
    }
    canon = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    checksum = hashlib.sha256(canon.encode()).hexdigest()
    out = os.path.abspath(a.out); os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"payload": payload, "sha256": checksum}, open(out, "w"), indent=2)
    open(out + ".sha256", "w").write(checksum + "\n")
    print(f"[build_manifest] wrote {out}")
    print(f"  sha256 = {checksum}")
    print(f"  grid: {payload['grid']}")
    print(f"  identifiability: {ident}")
    print(f"  floor: {floor} (max_rep={max_rep}) | run×donor: {run_donor_status}")
    print(f"  NTC: {payload['ntc']} | singletons(n_cells=1): {payload['measurement_error']['n_singleton_cells']}")

if __name__ == "__main__":
    main()
