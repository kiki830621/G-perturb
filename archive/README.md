# archive

Exploratory work that did not make it into the final pipeline, kept for the record.

## `analysis/` — count-native effect model (issues #19, #20)

`count_recovery.R`, `fold_recovery.py`, and `fold_realdata_subset.py` test a count-native
effect estimate (a negative-binomial / Poisson log-fold-change with a library-size offset)
as an alternative to the shipped plug-in log-CPM contrast. On synthetic data the count model
recovers a known multiplicative fold more accurately at low counts, but on the real data,
once low-count-gene noise is handled, it leaves the target ranking essentially unchanged:
the naive-fold lift is low-count noise, precision-weighting shows no advantage, and
empirical-Bayes shrinkage is unstable on the raw fold. So the shipped estimator stands, and
this is the effect-estimator robustness note in the manuscript's Limitations section. The
scripts run reproducibly but are not part of the ranking pipeline.
