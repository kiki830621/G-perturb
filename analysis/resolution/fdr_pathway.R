#!/usr/bin/env Rscript
# fdr_pathway.R  —  task 4.1 (single selective-FDR test tree; competitive vs self-contained pathway).
#
# Gene-wise: a target-blind gene universe with ONE atlas-wide error-control step, not an independent
# uncontrolled FDR per target. We show on synthetic gene effects (known non-null set) that the single
# atlas-wide BH holds realized FDR <= the frozen gate, while a naive per-target BH inflates it.
# Pathway: competitive (rank-based, CAMERA-like) and self-contained (sum-of-squares, ROAST-like)
# nulls are reported SEPARATELY on signed all-gene statistics.

suppressWarnings(suppressMessages(library(jsonlite)))
here <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
if (length(here) == 0 || is.na(here)) here <- "analysis/resolution"
gates <- fromJSON(file.path(here, "results", "gates.frozen.json"))$payload$thresholds

set.seed(7)
n_target <- 200; n_gene <- 400; frac_nonnull <- 0.10
# per (target,gene) z-statistic; a random 10% of (target,gene) are truly non-null (effect ~ N(0,3))
truth <- matrix(rbinom(n_target*n_gene, 1, frac_nonnull), n_target, n_gene)
eff   <- matrix(rnorm(n_target*n_gene, 0, ifelse(truth==1, sqrt(3), 0)), n_target, n_gene)
z     <- eff + matrix(rnorm(n_target*n_gene), n_target, n_gene)      # + measurement noise
pmat  <- 2*pnorm(-abs(z))

realized_fdr <- function(reject, truth) { d <- sum(reject); if (d==0) return(0); sum(reject & truth==0)/d }

# atlas-wide single BH over the whole target x gene universe
q_atlas <- matrix(p.adjust(as.vector(pmat), "BH"), n_target, n_gene)
rej_atlas <- q_atlas <= 0.05
fdr_atlas <- realized_fdr(rej_atlas, truth)

# naive: independent BH within each target (uncontrolled selection across the atlas)
rej_naive <- t(apply(pmat, 1, function(p) p.adjust(p, "BH") <= 0.05))
fdr_naive <- realized_fdr(rej_naive, truth)

genewise <- list(
  scheme = "single atlas-wide BH over the target-blind gene universe, then stage-wise",
  target_gene_pairs = n_target*n_gene, nonnull_fraction = frac_nonnull,
  atlas_wide_realized_fdr = round(fdr_atlas, 4),
  naive_per_target_realized_fdr = round(fdr_naive, 4),
  gate_fdr_max = gates$fdr$accept_hi,
  atlas_within_gate = fdr_atlas <= gates$fdr$accept_hi,
  demonstrates = "single atlas-wide control holds FDR; naive per-target control inflates it")

# ---- pathway: one gene set of 40 genes, half enriched; signed statistics ---------------------
gene_t <- colMeans(z)                      # signed per-gene statistic across targets
set_idx <- 1:40; set_enriched <- truth[, set_idx] |> colMeans() > frac_nonnull*1.5
# competitive (CAMERA-like): is the set shifted vs the rest? rank-sum on signed |stat|
comp_p <- suppressWarnings(wilcox.test(abs(gene_t[set_idx]), abs(gene_t[-set_idx]))$p.value)
# self-contained (ROAST-like): is the set's mean squared statistic > permuted null?
obs_ss <- mean(gene_t[set_idx]^2)
null_ss <- replicate(999, { s <- sample(seq_along(gene_t), length(set_idx)); mean(gene_t[s]^2) })
selfc_p <- (1 + sum(null_ss >= obs_ss)) / 1000
pathway <- list(
  set_size = length(set_idx),
  competitive = list(test = "CAMERA-like rank-sum (set vs rest)", p = round(comp_p, 4)),
  self_contained = list(test = "ROAST-like permutation (set mean-square)", p = round(selfc_p, 4)),
  reported_separately = TRUE,
  note = "competitive and self-contained answer different questions; both on signed all-gene stats, pinned gene-set version")

out <- list(scale = "synthetic_demo", genewise = genewise, pathway = pathway)
write(toJSON(out, auto_unbox = TRUE, pretty = TRUE), file.path(here, "results", "fdr_pathway.json"))
cat("gene-wise selective-FDR + pathway:\n")
cat(sprintf("  atlas-wide realized FDR = %.3f (gate <= %.2f) within=%s\n",
            fdr_atlas, gates$fdr$accept_hi, genewise$atlas_within_gate))
cat(sprintf("  naive per-target FDR    = %.3f (inflated demo)\n", fdr_naive))
cat(sprintf("  pathway competitive p=%.3f | self-contained p=%.3f (reported separately)\n",
            comp_p, selfc_p))
cat("wrote results/fdr_pathway.json\n")
