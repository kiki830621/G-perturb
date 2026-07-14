#!/usr/bin/env python3
"""fold_recovery.py  —  issue #19: does a count model recover the TRUE fold-change (multiplicative
effect) better than the shipped plug-in log-CPM, especially at low counts?

The point (review): a count model's real advantage is the interpretable *multiplicative* effect, a
fold = exp(beta) in log(mu) = log(library size) + beta. The shipped effect is
log1p(count / total_counts * 1e6) minus a non-targeting-control (NTC) reference — it averages the
log1p of per-pseudobulk CPMs. By Jensen's inequality (log1p is concave) that averaging attenuates the
fold toward 0, worst where counts are low. The count GLM instead takes the log of the *pooled* rate
(total counts / total library size per group), which is the exact Poisson/NB-GLM MLE for a two-group
log-link model (identical for Poisson and NB — the group-rate MLE is the sufficient-statistic ratio,
independent of the dispersion), and is (near-)unbiased for the true fold.

We simulate perturbations with a KNOWN true log-fold-change over a well-covered NTC baseline, across
coverage levels (perturbation n_cells), and compare fold recovery: bias + RMSE of each estimator vs
the true fold. Pure NumPy, closed-form — no GLM fitting needed.

  env FR_REPS (default 4000)  FR_LFC (default 1.0)  FR_THETA (default 3.0)
"""
import json
import os

import numpy as np

RNG = np.random.default_rng(0)
TRUE_LFC = float(os.environ.get("FR_LFC", "1.0"))   # ~2.7-fold true effect
R0 = 3e-4                                            # baseline expression rate
DEPTH = 4000                                         # per-cell library depth
THETA = float(os.environ.get("FR_THETA", "3.0"))    # NB dispersion (size); larger = closer to Poisson
K_PERT = 4                                           # perturbation replicates (e.g. donors)
M_NTC = 40                                           # NTC pool size
NTC_NCELLS = 80                                      # NTC coverage (well covered)
REPS = int(os.environ.get("FR_REPS", "4000"))
COVERAGE = [1, 2, 3, 5, 10, 20, 50, 100]            # perturbation n_cells (singleton -> well covered)


def nb(mu: np.ndarray, size: float, n: int) -> np.ndarray:
    """NB counts with mean mu, dispersion size (numpy param: p = size / (size + mu))."""
    p = size / (size + mu)
    return RNG.negative_binomial(size, p, n)


def one_draw(ncell_pert: int) -> tuple[float, float]:
    """Return (count-GLM fold, plug-in log-CPM fold) for one simulated perturbation vs NTC pool."""
    # NTC pool, well covered
    L_N = np.full(M_NTC, NTC_NCELLS * DEPTH, float)
    c_N = nb(L_N * R0, THETA, M_NTC)
    # perturbation: K replicates at this coverage, true multiplicative effect exp(TRUE_LFC)
    L_P = np.full(K_PERT, ncell_pert * DEPTH, float)
    c_P = nb(L_P * R0 * np.exp(TRUE_LFC), THETA, K_PERT)
    # count-GLM fold = log(pooled pert rate / pooled NTC rate) = exact Poisson/NB-GLM MLE
    rate_P = c_P.sum() / L_P.sum()
    rate_N = c_N.sum() / L_N.sum()
    fold_glm = np.log(rate_P) - np.log(rate_N) if (rate_P > 0 and rate_N > 0) else np.nan
    # plug-in log-CPM fold = mean_rep log1p(CPM) - mean_NTC log1p(CPM)  (matches prep_effects.py)
    fold_plug = np.log1p(c_P / L_P * 1e6).mean() - np.log1p(c_N / L_N * 1e6).mean()
    return fold_glm, fold_plug


def summarize(est: np.ndarray) -> dict:
    est = est[np.isfinite(est)]
    return {
        "n": int(est.size),
        "bias": round(float(est.mean() - TRUE_LFC), 4),
        "rmse": round(float(np.sqrt(np.mean((est - TRUE_LFC) ** 2))), 4),
        "undefined_frac": None,  # filled by caller
    }


def main() -> None:
    print(f"fold_recovery: reps={REPS} true_logFC={TRUE_LFC} (fold={np.exp(TRUE_LFC):.2f}x) theta={THETA}")
    print(f"{'n_cells':>8} | {'count-GLM bias':>14} {'rmse':>6} | {'plug-in bias':>12} {'rmse':>6}  <- attenuation")
    rows = []
    for nc in COVERAGE:
        draws = np.array([one_draw(nc) for _ in range(REPS)])
        glm_raw, plug = draws[:, 0], draws[:, 1]
        glm = glm_raw[np.isfinite(glm_raw)]
        g = summarize(glm_raw)
        p = summarize(plug)
        g["undefined_frac"] = round(float(np.mean(~np.isfinite(glm_raw))), 4)
        print(f"{nc:>8} | {g['bias']:>+14.3f} {g['rmse']:>6.3f} | {p['bias']:>+12.3f} {p['rmse']:>6.3f}")
        rows.append({"n_cells": nc, "count_glm": g, "plug_in": p})
    out = {
        "issue": 19,
        "true_logFC": TRUE_LFC,
        "true_fold": round(float(np.exp(TRUE_LFC)), 3),
        "theta": THETA,
        "reps": REPS,
        "criterion": "fold-change (multiplicative effect) recovery vs known truth; count-GLM fold = "
        "log(pooled rate ratio) = exact Poisson/NB-GLM MLE; plug-in = mean log1p(CPM) difference",
        "rows": rows,
    }
    here = os.path.dirname(os.path.abspath(__file__))
    dst = os.path.join(here, "results", "synthetic_recovery", "fold_recovery.json")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote results/synthetic_recovery/fold_recovery.json")


if __name__ == "__main__":
    main()
