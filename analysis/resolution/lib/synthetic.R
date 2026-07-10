# synthetic.R  —  synthetic generalizability-theory data with KNOWN variance components.
# Supports tasks 3.x (inference-contract calibration) and 6.2 (synthetic recovery / method selection).
#
# Design mirrors the real facet structure (CLAUDE.md / docs/design.md):
#   Target (random, the object of reliability) × Guide (random, NESTED within target)
#   × Donor (random, CROSSED) × Condition (FIXED domain).
# Pseudobulk measurement error is heteroscedastic: a cell aggregating n_cells single cells has
# effect-estimate variance sigma2_within / n_cells (this is the B-005 structure the GLS stage uses).
#
# Model for the cell-level pseudobulk summary y_{tgdc}:
#   y = mu + a_t + b_{t,g} + c_{t,d} + phi_c + e_{tgdc} + meas_err
#     a_t     ~ N(0, s2_T)     target main            (true reliability signal)
#     b_{t,g} ~ N(0, s2_TG)    target x guide         (guide heterogeneity within target)
#     c_{t,d} ~ N(0, s2_TD)    target x donor         (donor generalizability)
#     phi_c                    fixed condition effect (fixed facet)
#     e       ~ N(0, s2_res)   residual (highest-order interaction + sampling)
#     meas_err~ N(0, s2_within / n_cells)   pseudobulk measurement error (heteroscedastic)
#
# Returns list(df, truth, meta). `truth` are the variance-component SHARES of the random part
# (excluding the fixed condition and the measurement error, which is a known nuisance).

simulate_gtheory <- function(n_target = 40, n_guide = 2, n_donor = 4, n_cond = 3,
                             s2_T = 1.0, s2_TG = 0.25, s2_TD = 0.35, s2_res = 0.30,
                             s2_within = 1.5,
                             cell_sizes = NULL,   # per-cell n_cells; default lognormal 20..400
                             dist = c("gaussian", "heavy"),
                             seed = 1L) {
  dist <- match.arg(dist)
  set.seed(seed)

  grid <- expand.grid(target = factor(seq_len(n_target)),
                      guide  = factor(seq_len(n_guide)),
                      donor  = factor(seq_len(n_donor)),
                      cond   = factor(seq_len(n_cond)),
                      KEEP.OUT.ATTRS = FALSE, stringsAsFactors = TRUE)
  N <- nrow(grid)

  # cell sizes -> heteroscedastic measurement error
  if (is.null(cell_sizes)) {
    cell_sizes <- pmax(5, round(rlnorm(N, meanlog = log(80), sdlog = 0.7)))
  }
  grid$n_cells <- cell_sizes

  rnd <- if (dist == "heavy") function(n, sd) rt(n, df = 4) * sd / sqrt(4 / 2) else
                                   function(n, sd) rnorm(n, sd = sd)

  a_t   <- rnd(n_target, sqrt(s2_T));                 names(a_t)  <- levels(grid$target)
  # guide nested within target: one draw per (target,guide)
  tg_key <- paste(grid$target, grid$guide, sep = ":")
   utg    <- unique(tg_key); b_tg <- rnd(length(utg), sqrt(s2_TG)); names(b_tg) <- utg
  # donor crossed: one draw per (target,donor)
  td_key <- paste(grid$target, grid$donor, sep = ":")
  utd    <- unique(td_key); c_td <- rnd(length(utd), sqrt(s2_TD)); names(c_td) <- utd
  phi_c  <- rnorm(n_cond, sd = 0.5);                  names(phi_c) <- levels(grid$cond)

  e      <- rnd(N, sqrt(s2_res))
  meas   <- rnorm(N, sd = sqrt(s2_within / grid$n_cells))

  grid$y_true <- 2.0 + a_t[grid$target] + b_tg[tg_key] + c_td[td_key] + phi_c[grid$cond] + e
  grid$y      <- grid$y_true + meas
  grid$me_var <- s2_within / grid$n_cells   # KNOWN measurement-error variance (matched-NTC estimable)

  denom <- s2_T + s2_TG + s2_TD + s2_res
  truth <- c(T = s2_T, TG = s2_TG, TD = s2_TD, res = s2_res) / denom

  list(df = grid,
       truth = truth,
       meta = list(n = N, dist = dist,
                   components = c(s2_T = s2_T, s2_TG = s2_TG, s2_TD = s2_TD,
                                  s2_res = s2_res, s2_within = s2_within)))
}
