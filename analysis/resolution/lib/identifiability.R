# identifiability.R  —  tasks 2.1 / 2.2  (spec: "Empirical identifiability is a fail-closed gate").
#
# Two gates over the ACTUAL cell table (never over assumed structure):
#   design_rank_gate      : does the realized incidence have the rank to separate each claimed
#                           component from the others and from residual? A component whose
#                           interaction has < 2 realized levels, or whose variation is fully
#                           absorbed (no residual df), is `not_identifiable`.
#   separability_gate     : are two facets confounded (one a deterministic function of the other,
#                           e.g. donor perfectly aliased with sequencing run)?
#   replication_floor_gate: does an identical-spec replicate exist (same target,guide,donor,cond
#                           in >1 row)? If not, the floor is `not_identifiable` and the highest-
#                           order interaction is combined with sampling residual.
#
# All gates FAIL CLOSED: on any deficiency the status is a downgrade, never a fabricated number.

# terms: named list of factor-column vectors, FIRST column is the anchor facet (target) which is
# never dropped, e.g.
#   list(T="target", TG=c("target","guide"), TD=c("target","donor"), TGD=c("target","guide","donor"))
# A term is identifiable only if its realized interaction has MORE levels than every "parent" it
# obtains by dropping one non-anchor factor — i.e. the added facet genuinely varies within the
# coarser grouping. (Marginal data where guide is aggregated to one level fails here: lv(TG)==lv(T).)
design_rank_gate <- function(df, terms) {
  N <- nrow(df)
  n_levels <- function(cols) nlevels(interaction(df[cols], drop = TRUE))
  full_cols <- unique(unlist(terms))
  n_finest  <- nlevels(interaction(df[full_cols], drop = TRUE))
  df_resid  <- N - n_finest                    # > 0  <=>  some finest cell is replicated

  status <- lapply(names(terms), function(nm) {
    cols <- terms[[nm]]; lv <- n_levels(cols)
    if (lv < 2) return("not_identifiable")
    droppable <- cols[-1]                       # anchor (first col) is never dropped
    if (length(droppable) == 0) return("empirically_passed")   # main effect of anchor
    parent_lv <- vapply(droppable, function(f) n_levels(setdiff(cols, f)), numeric(1))
    if (lv > max(parent_lv)) "empirically_passed" else "not_identifiable"
  })
  names(status) <- names(terms)
  list(term_status = status, n = N, n_finest_cells = n_finest, df_resid = df_resid)
}

# a and b are column names; b is confounded within a if every level of a maps to exactly one level of b
separability_gate <- function(df, a, b) {
  tab <- table(df[[a]], df[[b]])
  # each row (level of a) touches how many columns (levels of b)?
  per_a <- rowSums(tab > 0)
  per_b <- colSums(tab > 0)
  aliased <- all(per_a <= 1) || all(per_b <= 1)   # one is a function of the other
  list(pair = c(a, b), aliased = aliased,
       status = if (aliased) "not_identifiable" else "empirically_passed",
       max_b_per_a = max(per_a), max_a_per_b = max(per_b))
}

replication_floor_gate <- function(df, spec_cols = c("target","guide","donor","cond")) {
  spec_cols <- spec_cols[spec_cols %in% names(df)]
  counts <- table(interaction(df[spec_cols], drop = TRUE))
  max_rep <- max(counts)
  list(spec = spec_cols, max_replicate = as.integer(max_rep),
       status = if (max_rep >= 2) "empirically_passed" else "not_identifiable",
       note = if (max_rep < 2)
                "no identical-spec replicate: floor not_identifiable; combine highest-order interaction with sampling residual"
              else "identical-spec replicate present")
}
