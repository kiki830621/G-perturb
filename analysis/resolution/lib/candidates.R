# candidates.R  —  the three profile-decomposition candidates (docs/design.md Decision 6).
# Each estimator maps a synthetic/real cell table to variance-component SHARES over
# {T, TG, TD, res}. They differ in principle so that pre-registered synthetic recovery
# (task 6.2) can select ONE on synthetic loss alone — never on external validation.
#
#   PWM  precision_weighted_multivariate : inverse-measurement-error-weighted REML mixed model,
#        with matched measurement-error REMOVAL from the residual (the B-005 GLS contract).
#   KDP  kernel_distance_permutational   : Euclidean/PERMANOVA sum-of-squares partition (adonis2-
#        equivalent for a univariate summary). A DISTANCE attribution, reported as DIAGNOSTIC —
#        it is not a variance component without a PSD+additivity proof (CLAUDE.md "prove before
#        you name"). Recovery will show empirically whether SS-share == variance-share.
#   RHF  robust_hierarchical_functional  : heavy-tail-robust mixed model (IRLS down-weighting of
#        outlying cells) + measurement-error removal.
#
# All three are boundary-aware: a negative component after me-removal is floored at 0 (does not
# silently redefine the estimand) and flagged.

suppressWarnings(suppressMessages(library(lme4)))

.shares <- function(v) {
  nm <- names(v); v <- pmax(0, v)
  out <- if (sum(v) <= 0) v * 0 else v / sum(v)
  setNames(out, nm)
}

# extract (target, target:guide, target:donor, residual) variances from a fitted lmer
.varcomp <- function(fit) {
  vc <- as.data.frame(VarCorr(fit))
  g  <- function(grp) { x <- vc$vcov[vc$grp == grp & is.na(vc$var2)]; if (length(x)) x[1] else 0 }
  c(T   = g("target"),
    TG  = g("target:guide"),
    TD  = g("target:donor"),
    res = g("Residual"))
}

# ---- PWM ------------------------------------------------------------------------------------
# REML mixed model with the B-005 measurement-error GLS contract: the KNOWN per-cell measurement
# error (me_var) is REMOVED from the estimated residual (the precision/second-stage correction),
# so the residual share estimates s2_res rather than s2_res + measurement noise. Boundary-aware.
est_pwm <- function(df) {
  ok <- tryCatch({
    fit <- lmer(y ~ cond + (1 | target) + (1 | target:guide) + (1 | target:donor),
                data = df, REML = TRUE,
                control = lmerControl(check.conv.singular = .makeCC("ignore", tol = 1e-4)))
    v <- .varcomp(fit)
    neg <- (v["res"] - mean(df$me_var)) < 0
    v["res"] <- max(0, v["res"] - mean(df$me_var))   # measurement-error removal
    list(shares = .shares(v), neg = unname(neg), ok = TRUE)
  }, error = function(e) list(shares = c(T=NA,TG=NA,TD=NA,res=NA), neg = NA, ok = FALSE))
  ok
}

# ---- KDP (distance/PERMANOVA SS partition; diagnostic) --------------------------------------
# Euclidean univariate PERMANOVA pseudo-F reduces to ANOVA SS. We partition the sequential
# (Type-I) SS over cond -> target -> target:guide -> target:donor and report the random-term SS
# shares. Computed by an O(N) group-mean SWEEP (residualize onto each factor's cell means in turn)
# instead of aov()'s dense N x (~4200-column) design matrix — mathematically the same Type-I SS for
# this hierarchical design, but seconds not minutes at n_target=600. This is the "1 - CCC / distance"
# family: a share, NOT a proven variance component.
est_kdp <- function(df) {
  ok <- tryCatch({
    ctr <- function(r, grp) r - ave(r, grp, FUN = mean)      # project out grp cell means
    tg  <- interaction(df$target, df$guide, drop = TRUE)
    td  <- interaction(df$target, df$donor, drop = TRUE)
    r0 <- df$y - mean(df$y);         s0 <- sum(r0^2)
    r1 <- ctr(r0, df$cond);          s1 <- sum(r1^2)
    r2 <- ctr(r1, df$target);        s2 <- sum(r2^2)
    r3 <- ctr(r2, tg);               s3 <- sum(r3^2)
    r4 <- ctr(r3, td);               s4 <- sum(r4^2)
    v <- c(T = s1 - s2, TG = s2 - s3, TD = s3 - s4, res = s4)
    list(shares = .shares(v), neg = FALSE, ok = TRUE)
  }, error = function(e) list(shares = c(T=NA,TG=NA,TD=NA,res=NA), neg = NA, ok = FALSE))
  ok
}

# ---- RHF (robust hierarchical) --------------------------------------------------------------
# One IRLS pass: fit lmer, down-weight cells with large standardized residuals (Huber-style),
# refit; then measurement-error removal. Robust to the heavy-tail scenario.
est_rhf <- function(df) {
  ok <- tryCatch({
    ctrl <- lmerControl(check.conv.singular = .makeCC("ignore", tol = 1e-4))
    fit0 <- lmer(y ~ cond + (1|target) + (1|target:guide) + (1|target:donor),
                 data = df, REML = TRUE, control = ctrl)
    r  <- resid(fit0); s <- mad(r); k <- 1.345 * s
    w  <- ifelse(abs(r) <= k, 1, k / abs(r))          # Huber weights (down-weight outlying cells)
    w  <- w / mean(w)                                  # normalize to mean 1 (keep residual scale)
    fit <- lmer(y ~ cond + (1|target) + (1|target:guide) + (1|target:donor),
                data = df, weights = w, REML = TRUE, control = ctrl)
    v <- .varcomp(fit)
    neg <- (v["res"] - mean(df$me_var)) < 0
    v["res"] <- max(0, v["res"] - mean(df$me_var))    # measurement-error removal
    list(shares = .shares(v), neg = unname(neg), ok = TRUE)
  }, error = function(e) list(shares = c(T=NA,TG=NA,TD=NA,res=NA), neg = NA, ok = FALSE))
  ok
}

CANDIDATES <- list(
  precision_weighted_multivariate = est_pwm,
  kernel_distance_permutational   = est_kdp,
  robust_hierarchical_functional  = est_rhf
)
