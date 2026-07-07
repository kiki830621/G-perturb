#!/usr/bin/env python3
"""Validate CODEBOOK.json against the actual downloaded CSVs.

Independent of build_codebook.py: re-reads each CSV header and asserts every column
is documented in CODEBOOK.json, that each facet (donor / condition / guide / target)
is reachable, and that the reliability-field gap is recorded. Exit 0 = pass, 1 = fail.
This is the verification gate for issue #1 (data acquisition + codebook).

Run:  python3 validate_codebook.py
"""
from __future__ import annotations
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
CODEBOOK = os.path.join(HERE, "CODEBOOK.json")


def fail(msg: str) -> None:
    print(f"  ✗ {msg}")


def main() -> int:
    if not os.path.exists(CODEBOOK):
        print(f"✗ {CODEBOOK} missing — run build_codebook.py first")
        return 1
    with open(CODEBOOK) as f:
        cb = json.load(f)

    errors = 0
    downloaded = cb.get("files_downloaded", {})

    # 1. Every column in each raw CSV must be documented.
    for fname, block in downloaded.items():
        path = os.path.join(RAW, fname)
        if not os.path.exists(path):
            fail(f"{fname}: documented but not present in raw/ (run fetch_data.sh)")
            errors += 1
            continue
        with open(path, newline="") as f:
            header = next(csv.reader(f))
        # pandas names an empty first header 'Unnamed: 0'; normalise for comparison
        header = [h if h else "Unnamed: 0" for h in header]
        documented = {fld["name"] for fld in block["fields"]}
        missing = [c for c in header if c not in documented]
        if missing:
            fail(f"{fname}: {len(missing)} column(s) not in codebook: {missing}")
            errors += 1
        else:
            print(f"  ✓ {fname}: all {len(header)} columns documented")

    # 2. Each facet must be reachable somewhere in the codebook.
    all_roles = set()
    for block in downloaded.values():
        for fld in block["fields"]:
            all_roles.add(fld.get("facet_role"))
    for prod in cb.get("products_not_downloaded", {}).values():
        for fld in prod.get("documented_fields", []):
            all_roles.add(fld.get("facet_role"))
    for facet in ("target", "guide", "donor", "condition"):
        if facet not in all_roles:
            fail(f"facet '{facet}' has no column with facet_role='{facet}'")
            errors += 1
        else:
            print(f"  ✓ facet '{facet}' reachable")

    # 3. Reliability gap must be documented (the key #1 finding).
    reliability_cols = {
        f["name"]
        for prod in cb.get("products_not_downloaded", {}).values()
        for f in prod.get("documented_fields", [])
        if f.get("facet_role") == "reliability"
    }
    flat = downloaded.get("DE_stats.suppl_table.csv", {})
    flat_cols = {fld["name"] for fld in flat.get("fields", [])}
    if not reliability_cols:
        fail("no reliability fields documented in products_not_downloaded")
        errors += 1
    elif reliability_cols & flat_cols:
        fail(f"reliability fields unexpectedly present in flat CSV: {reliability_cols & flat_cols}")
        errors += 1
    else:
        print(f"  ✓ reliability gap recorded ({len(reliability_cols)} fields live outside the flat CSV)")

    gaps = cb.get("known_gaps", [])
    if not any("reduced" in g.lower() or "reliability" in g.lower() for g in gaps):
        fail("known_gaps does not mention the reduced-CSV / reliability gap")
        errors += 1
    else:
        print("  ✓ known_gaps notes the reduced-CSV reliability gap")

    print()
    if errors:
        print(f"✗ CODEBOOK validation FAILED ({errors} error(s))")
        return 1
    print("✓ CODEBOOK validation PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
