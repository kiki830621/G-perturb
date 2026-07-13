#!/usr/bin/env Rscript
# count_recovery.R  —  issue #19: count-native (NB-GLMM) vs shipped (plug-in-logCPM + Gaussian)
# variance-component recovery, and Poisson vs NB, on COUNT-generated data with low-count rows.
#
# WHY (issue #19): the pseudobulk .X is raw counts. The shipped pipeline derives a plug-in
# log-CPM effect and decomposes its variance with a Gaussian mixed model + explicit measurement-
# error removal (est_pwm). A count-native model instead keeps the counts and uses an NB-GLMM with
# a library-size offset: the NB dispersion theta absorbs pure count-sampling noise while an
# observation-level random effect (OLRE) absorbs the biological residual s2_res — so measurement
# error is separated STRUCTURALLY, no me-removal needed. Poisson lacks theta, so its OLRE conflates
# sampling overdispersion with s2_res. This harness tests, on data where the truth is KNOWN:
#   * does NB-GLMM recover {T,TG,TD,res} at least as well as the shipped est_pwm?
#   * where do they diverge — is it the low-count / singleton regime (the hypothesis)?
#   * how much does Poisson mis-attribute vs NB?
#
# Pre-registered sub-experiment (does NOT touch the frozen 3-candidate selection in candidates.R).
# LOCAL run is a SMOKE (glmer.nb is expensive); full scale (reps>=2000, realistic n_target) is a
# cluster job. Output labels scale honestly and never claims a gate pass locally.
#
#   env CR_REPS (default 20)  CR_NTARGET (default 60)  CR_THETA (default 3)  CR_CORES
# Truth {s2_T,s2_TG,s2_TD,s2_res} are variance components on the LOG-MEAN scale.

suppressWarnings(suppressMessages({ library(lme4); library(MASS); library(jsonlite); library(parallel) }))

here <- tryCatch(dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1])),
                 error = function(e) "analysis/resolution")
if (length(here) == 0 || is.na(here)) here <- "analysis/resolution"
source(file.path(here, "lib", "candidates.R"))   # reuse est_pwm (the shipped estimator)

REPS    <- as.integer(Sys.getenv("CR_REPS", "20"))
NTARGET <- as.integer(Sys.getenv("CR_NTARGET", "60"))
THETA   <- as.numeric(Sys.getenv("CR_THETA", "3"))       # NB size; smaller = more overdispersed
NCORES  <- as.integer(Sys.getenv("CR_CORES", as.character(max(1, detectCores() - 2))))
comps   <- c("T", "TG", "TD", "res")

# ---- count generator: KNOWN log-mean components, library size tied to n_cells --------------
# log(mu_i) = log(lib_i) + log(base_rate) + a_t + b_tg + c_td + phi_c + resid_i
#   count_i ~ NB(mu_i, theta)         (Poisson as theta -> Inf)
# Two coverage regimes set how many cells (hence library size) each pseudobulk aggregates:
#   "covered"   : n_cells lognormal ~ median 80  (log-CPM is a good approximation)
#   "singleton" : n_cells heavy at 1-5           (log-CPM breaks; count model should help)
simulate_counts <- function(n_target, regime, theta,
                            s2_T = 1.0, s2_TG = 0.25, s2_TD = 0.35, s2_res = 0.30,
                            n_guide = 2, n_donor = 4, n_cond = 3,
                            base_rate = 3e-4, per_cell_depth = 4000, seed = 1L) {
  set.seed(seed)
  grid <- expand.grid(target = factor(seq_len(n_target)), guide = factor(seq_len(n_guide)),
                      donor = factor(seq_len(n_donor)), cond = factor(seq_len(n_cond)),
                      KEEP.OUT.ATTRS = FALSE, stringsAsFactors = TRUE)
  N <- nrow(grid)
  if (regime == "singleton") {
    n_cells <- pmax(1, rnbinom(N, size = 0.6, mu = 3))          # heavy at 1-5, many singletons
  } else {
    n_cells <- pmax(5, round(rlnorm(N, meanlog = log(80), sdlog = 0.7)))
  }
  lib <- pmax(1, n_cells * per_cell_depth)                       # library size = obs total_counts
  a_t  <- rnorm(n_target, sd = sqrt(s2_T));  names(a_t)  <- levels(grid$target)
  tg   <- paste(grid$target, grid$guide, sep = ":"); utg <- unique(tg)
  b_tg <- rnorm(length(utg), sd = sqrt(s2_TG)); names(b_tg) <- utg
  td   <- paste(grid$target, grid$donor, sep = ":"); utd <- unique(td)
  c_td <- rnorm(length(utd), sd = sqrt(s2_TD)); names(c_td) <- utd
  phi  <- rnorm(n_cond, sd = 0.5); names(phi) <- levels(grid$cond)
  resid <- rnorm(N, sd = sqrt(s2_res))                          # biological highest-order residual
  eta  <- log(base_rate) + a_t[grid$target] + b_tg[tg] + c_td[td] + phi[grid$cond] + resid
  mu   <- lib * exp(eta)
  count <- if (is.finite(theta)) rnbinom(N, size = theta, mu = mu) else rpois(N, mu)
  denom <- s2_T + s2_TG + s2_TD + s2_res
  grid$n_cells <- n_cells; grid$lib <- lib; grid$count <- count; grid$obs <- factor(seq_len(N))
  # derived log-CPM effect + delta-method measurement-error variance (what the shipped path uses)
  grid$y <- log1p(count / lib * 1e6)
  grid$me_var <- 1 / pmax(count, 0.5) + if (is.finite(theta)) 1 / theta else 0
  list(df = grid, truth = c(T = s2_T, TG = s2_TG, TD = s2_TD, res = s2_res) / denom)
}

# ---- count-native candidates: shares over {T, TG, TD, res=OLRE} on the link scale ----------
.count_shares <- function(fit) {
  vc <- as.data.frame(VarCorr(fit))
  g <- function(grp) { x <- vc$vcov[vc$grp == grp & is.na(vc$var2)]; if (length(x)) x[1] else 0 }
  v <- c(T = g("target"), TG = g("target:guide"), TD = g("target:donor"), res = g("obs"))
  nm <- names(v); v <- pmax(0, v)   # pmax() strips names — capture nm first (mirrors .shares in candidates.R)
  if (sum(v) <= 0) return(setNames(v * 0, nm))
  setNames(v / sum(v), nm)
}
# offset lives INSIDE the formula so `lib` is evaluated in data=df (not the calling frame)
FORM <- count ~ cond + (1 | target) + (1 | target:guide) + (1 | target:donor) + (1 | obs) +
  offset(log(lib))
CTRL <- glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 3e4),
                     check.conv.singular = .makeCC("ignore", tol = 1e-4))

est_nbglmm <- function(df) tryCatch({
  fit <- suppressWarnings(glmer.nb(FORM, data = df, control = CTRL))
  list(shares = .count_shares(fit), ok = TRUE)
}, error = function(e) list(shares = setNames(rep(NA, 4), comps), ok = FALSE, err = conditionMessage(e)))

est_poisglmm <- function(df) tryCatch({
  fit <- suppressWarnings(glmer(FORM, data = df, family = poisson, control = CTRL))
  list(shares = .count_shares(fit), ok = TRUE)
}, error = function(e) list(shares = setNames(rep(NA, 4), comps), ok = FALSE, err = conditionMessage(e)))

CANDS <- list(PWM_logCPM = est_pwm, NB_GLMM = est_nbglmm, POIS_GLMM = est_poisglmm)

# ---- run: two regimes, REPS each ------------------------------------------------------------
cat(sprintf("count_recovery SMOKE: reps=%d n_target=%d theta=%.1f cores=%d\n",
            REPS, NTARGET, THETA, NCORES))
regimes <- c("covered", "singleton")
summary_all <- list()
# PSOCK cluster (fork-safe: glmer.nb/theta.ml misbehaves under mclapply fork) — exploits all cores
USE_CLUSTER <- NCORES > 1
if (USE_CLUSTER) {
  cl <- makeCluster(NCORES)
  clusterEvalQ(cl, suppressWarnings(suppressMessages({ library(lme4); library(MASS) })))
  clusterExport(cl, c("simulate_counts", "est_pwm", "est_nbglmm", "est_poisglmm",
                      ".count_shares", ".shares", ".varcomp", "CANDS", "FORM", "CTRL",
                      "NTARGET", "THETA", "comps"))
}
for (rg in regimes) {
  one <- function(r) {
    sim <- simulate_counts(NTARGET, rg, THETA, seed = r)
    truth <- sim$truth[comps]
    lapply(names(CANDS), function(nm) {
      o <- CANDS[[nm]](sim$df)
      bad <- !isTRUE(o$ok) || any(is.na(o$shares))
      list(nm = nm, err = if (bad) rep(NA_real_, 4) else unname(o$shares[comps] - truth), fail = bad)
    })
  }
  t0 <- proc.time()[3]
  if (USE_CLUSTER) clusterExport(cl, "rg")   # rg is a for-loop global; ship it to workers each regime
  out <- if (USE_CLUSTER) parLapply(cl, seq_len(REPS), one) else lapply(seq_len(REPS), one)
  el <- round(proc.time()[3] - t0, 1)
  if (nzchar(Sys.getenv("CR_DEBUG"))) { r1 <- out[[1]]
    for (cc in r1) cat("DEBUG", rg, cc$nm, "err=[", paste(round(cc$err, 3), collapse=","),
                       "] len=", length(cc$err), " fail=", isTRUE(cc$fail), "\n") }
  err <- lapply(names(CANDS), function(x) matrix(NA_real_, REPS, 4, dimnames = list(NULL, comps)))
  names(err) <- names(CANDS); failc <- setNames(integer(length(CANDS)), names(CANDS))
  for (r in seq_along(out)) { rr <- out[[r]]; if (!is.list(rr)) next
    for (cr in rr) { if (isTRUE(cr$fail)) { failc[cr$nm] <- failc[cr$nm] + 1; next }; err[[cr$nm]][r, ] <- cr$err } }
  for (nm in names(CANDS)) {
    E <- err[[nm]]; E <- E[stats::complete.cases(E), , drop = FALSE]
    bias <- if (nrow(E)) colMeans(E) else setNames(rep(NA, 4), comps)
    rmse <- if (nrow(E)) sqrt(colMeans(E^2)) else setNames(rep(NA, 4), comps)
    summary_all[[length(summary_all) + 1]] <- list(
      regime = rg, candidate = nm, reps_effective = nrow(E), fit_failures = unname(failc[nm]),
      bias = as.list(round(bias, 4)), rmse = as.list(round(rmse, 4)),
      max_abs_bias = round(max(abs(bias)), 4), max_rmse = round(max(rmse), 4), elapsed_s = el)
    cat(sprintf("  [%-9s] %-11s bias=%.3f rmse=%.3f  (res bias=%+.3f) neff=%d fail=%d\n",
                rg, nm, max(abs(bias)), max(rmse), bias["res"], nrow(E), failc[nm]))
  }
}
if (exists("cl")) stopCluster(cl)
out_dir <- file.path(here, "results", "synthetic_recovery")
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
res <- list(scale = "smoke_only_not_a_gate_pass", issue = 19,
            reps = REPS, n_target = NTARGET, theta = THETA,
            note = "count-native NB-GLMM vs shipped plug-in-logCPM PWM; local smoke, NOT a gate pass; full scale (reps>=2000) is a cluster job",
            results = summary_all)
write(toJSON(res, auto_unbox = TRUE, pretty = TRUE, digits = 6, null = "null"),
      file.path(out_dir, "count_recovery_smoke.json"))
cat(sprintf("\nwrote results/synthetic_recovery/count_recovery_smoke.json (smoke)\n"))
