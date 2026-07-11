#!/usr/bin/env python3
"""prep_effects.py  —  issue #11 Phase 1: compute the NTC-relative perturbation effect matrix.

The pseudobulk .X is raw summed counts. The reliability object is the perturbation EFFECT, so we:
  1. log-CPM normalize each pseudobulk cell using its total_counts (library size),
  2. per (donor, condition, run) batch stratum, form the NTC reference = mean log-CPM over
     non-targeting guides (12/12 strata have NTC, min 827 each — verified),
  3. effect = log-CPM(cell) - NTC_ref(matched stratum), per gene.

Writes the effect matrix GENE-MAJOR as float32 binary so R can seek+read one gene's 278,684-vector
contiguously and fit the selected PWM model per gene in parallel. Fail-closed: no imputation; a cell
in a stratum lacking NTC would be dropped (does not occur here).

  env GENE_LIMIT (default all 18129)  — smoke on a gene subset
Output: realdata/effect.f32  (n_genes x n_obs, gene g at offset g*n_obs) + realdata/gene_names.txt
"""
import h5py, numpy as np, os, sys, time
from scipy.sparse import csr_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
H5 = os.path.join(HERE, "..", "..", "data", "raw", "GWCD4i.pseudobulk_merged.h5ad")
GENE_LIMIT = int(os.environ.get("GENE_LIMIT", "0"))  # 0 = all
CHUNK = int(os.environ.get("GENE_CHUNK", "1000"))
t0 = time.time()

def log(m): print(f"[prep {time.time()-t0:6.1f}s] {m}", flush=True)

f = h5py.File(H5, "r")
obs = f["obs"]
def cat(c):
    g = obs[c]; cats = [x.decode() if isinstance(x, bytes) else str(x) for x in g["categories"][:]]
    return np.array([cats[i] if i >= 0 else "" for i in g["codes"][:]], dtype=object)
donor, cond, run, gtype = cat("donor_id"), cat("culture_condition"), cat("10xrun_id"), cat("guide_type")
tc = obs["total_counts"][:].astype(np.float64)
n_obs = len(tc)
# batch stratum code (donor,cond,run) + NTC mask
strata = {}; stratum = np.empty(n_obs, dtype=np.int32)
for i in range(n_obs):
    k = (donor[i], cond[i], run[i]); stratum[i] = strata.setdefault(k, len(strata))
n_strata = len(strata)
ntc = (gtype == "non-targeting")
log(f"n_obs={n_obs} strata={n_strata} ntc_cells={int(ntc.sum())}")

# gene names
gene_names = [x.decode() if isinstance(x, bytes) else str(x) for x in f["var"]["_index"][:]]
n_gene_all = len(gene_names)
n_gene = n_gene_all if GENE_LIMIT == 0 else min(GENE_LIMIT, n_gene_all)
log(f"loading X (CSR {n_obs}x{n_gene_all})...")

X = f["X"]
Xcsr = csr_matrix((X["data"][:], X["indices"][:], X["indptr"][:]), shape=(n_obs, n_gene_all))
f.close()
log(f"loaded nnz={Xcsr.nnz}; normalizing (log-CPM in place)...")
# log-CPM on the CSR data: each nnz's row is known via repeated indptr expansion
rows = np.repeat(np.arange(n_obs), np.diff(Xcsr.indptr))
Xcsr.data = np.log1p(Xcsr.data / tc[rows] * 1e6).astype(np.float64)
del rows
log("converting to CSC for gene-column access...")
Xcsc = Xcsr.tocsc(); del Xcsr
log("CSC ready; computing NTC-relative effects + writing gene-major binary")

# precompute per-stratum row index lists (for NTC reference) and per-row stratum
ntc_rows_by_stratum = [np.where(ntc & (stratum == s))[0] for s in range(n_strata)]

out_path = os.path.join(HERE, "effect.f32")
with open(out_path, "wb") as fo:
    for g0 in range(0, n_gene, CHUNK):
        g1 = min(g0 + CHUNK, n_gene)
        D = Xcsc[:, g0:g1].toarray().astype(np.float64)          # n_obs x chunk (log-CPM)
        # NTC reference per stratum for these genes
        ref = np.zeros((n_strata, D.shape[1]))
        for s in range(n_strata):
            idx = ntc_rows_by_stratum[s]
            ref[s] = D[idx].mean(axis=0) if len(idx) else 0.0
        E = (D - ref[stratum]).astype(np.float32)                # effect = logCPM - matched NTC ref
        fo.write(np.asfortranarray(E).T.tobytes())               # gene-major: gene rows contiguous
        if g0 % (CHUNK * 5) == 0: log(f"  genes {g0}/{n_gene}")

with open(os.path.join(HERE, "gene_names.txt"), "w") as fn:
    fn.write("\n".join(gene_names[:n_gene]) + "\n")
np.save(os.path.join(HERE, "meta.npy"), dict(n_obs=n_obs, n_gene=n_gene, n_strata=n_strata))
log(f"DONE: wrote {out_path} ({n_gene} genes x {n_obs} obs, gene-major float32)")
