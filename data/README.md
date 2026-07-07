# Data

This project uses the **CD4+ T cell Perturb-seq** dataset from the Marson and Pritchard labs
(a suggested Researcher-track starting point for *Built with Claude: Life Sciences*, released
with code and preprint).

**Raw data is not committed** to this repository. Large single-cell / genomic files
(`*.h5ad`, `*.h5`, `*.loom`, `*.mtx`, …) and anything under `data/raw/` are gitignored.

## Layout

```
data/
├── raw/          # downloaded source data (gitignored)
└── processed/    # released summary statistics used by the analysis (small, may be committed)
```

## How to obtain

_Download links and fetch instructions to be filled in during the hackathon._
The analysis is designed to rerun on the **released summary statistics**, so a full raw
download is not required to reproduce the target ranking.
