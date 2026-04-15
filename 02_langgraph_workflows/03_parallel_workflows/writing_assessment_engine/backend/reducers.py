# =============================================================================
# reducers.py — Named reducer functions for the Writing Assessment Engine
#
# DIFFERENCE FROM state.py REDUCERS:
#   state.py has two tiny inline reducers (_take_new, _merge_dicts) that are
#   attached to TypedDict fields via Annotated[]. Those tell LangGraph how to
#   merge individual state fields during parallel execution automatically.
#
#   THIS FILE contains named, grouped reducer functions used explicitly inside
#   nodes (especially evaluation_merger_node) to consolidate related score
#   groups into structured summary dicts before writing back to state.
#
# PATTERN every reducer follows:
#   1. Guard against None  — a node might run before the other side has written
#   2. Merge with {**old, **new} — dict unpacking; new values win on key conflict
#   3. Return the merged result
#
# WHO USES THESE?
#   nodes.py  → evaluation_merger_node calls these to build dimension_breakdown
#   These are NOT attached to Annotated[] fields — they are called manually.
# =============================================================================

# -----------------------------------------------------------------------------
# merge_language_scores
#
# Merges scores for language-quality dimensions:
#   grammar, clarity, vocabulary, tone
#
# These four are grouped together because they all relate to HOW the writer
# uses language — word choice, sentence correctness, tone, and understandability.
#
# Called by: evaluation_merger_node to build the "language" section of
#            dimension_breakdown inside the final report.
#
# Args:
#   old (dict): previously accumulated language scores (may be None on first run)
#   new (dict): freshly computed language scores from the current merge pass
#
# Returns:
#   dict: merged language scores — new values override old on key conflict
#
# Example:
#   old = {"grammar": 7.5, "clarity": 6.0}
#   new = {"vocabulary": 8.0, "tone": 7.0}
#   result = {"grammar": 7.5, "clarity": 6.0, "vocabulary": 8.0, "tone": 7.0}
# -----------------------------------------------------------------------------

def merge_language_scores(old: dict | None, new: dict | None) -> dict:
    if old is None:
        return new
    if new is None:
        return old
    return {**old, **new}


# -----------------------------------------------------------------------------
# merge_argument_scores
#
# Merges fields from the argument_analysis dictionary:
#   claim_presence, supporting_evidence, reasoning_quality,
#   counterargument_usage, critical_thinking_depth
#
# The argument_structure_node returns a dict with these keys.
# This reducer ensures that if the analysis is built incrementally
# (e.g. in future multi-step argument nodes), no key is lost.
#
# Called by: evaluation_merger_node to attach argument quality data
#            to the dimension_breakdown output.
#
# Args:
#   old (dict): previously stored argument analysis fields
#   new (dict): newly computed argument analysis fields
#
# Returns:
#   dict: merged argument analysis — new values override old on key conflict
#
# Example:
#   old = {"claim_presence": True, "supporting_evidence": "weak"}
#   new = {"reasoning_quality": "strong", "counterargument_usage": False}
#   result = {
#       "claim_presence": True,
#       "supporting_evidence": "weak",
#       "reasoning_quality": "strong",
#       "counterargument_usage": False
#   }
# -----------------------------------------------------------------------------

def merge_argument_scores(old: dict | None, new: dict | None) -> dict:
    if old is None:
        return new
    if new is None:
        return old
    return {**old, **new}


# -----------------------------------------------------------------------------
# merge_structure_scores
#
# Merges scores for structural and organizational dimensions:
#   structure, coherence, depth
#
# These three are grouped because they all relate to HOW the writing is
# organized — whether ideas are arranged logically, flow smoothly, and
# explore the topic in sufficient depth.
#
# Called by: evaluation_merger_node to build the "structure" section of
#            dimension_breakdown inside the final report.
#
# Args:
#   old (dict): previously accumulated structure scores
#   new (dict): freshly computed structure scores
#
# Returns:
#   dict: merged structure scores — new values override old on key conflict
#
# Example:
#   old = {"structure": 8.0}
#   new = {"coherence": 7.5, "depth": 6.5}
#   result = {"structure": 8.0, "coherence": 7.5, "depth": 6.5}
# -----------------------------------------------------------------------------

def merge_structure_scores(old: dict | None, new: dict | None) -> dict:
    if old is None:
        return new
    if new is None:
        return old
    return {**old, **new}


# -----------------------------------------------------------------------------
# merge_final_evaluation
#
# Merges the top-level evaluation output:
#   final_score, dimension_breakdown
#
# This is the last merge that happens — after evaluation_merger_node has
# combined all group scores into a single evaluation summary, this reducer
# consolidates the overall score and the full breakdown dict together.
#
# Called by: evaluation_merger_node as the final step before writing
#            the merged result back into WritingState.
#
# Args:
#   old (dict): previously written evaluation (may be partial)
#   new (dict): newly computed evaluation fields
#
# Returns:
#   dict: merged final evaluation — new values override old on key conflict
#
# Example:
#   old = {"final_score": 0.0}
#   new = {
#       "final_score": 7.6,
#       "dimension_breakdown": {
#           "language":   {"grammar": 7.5, "clarity": 8.0, ...},
#           "structure":  {"structure": 8.0, "coherence": 7.5, ...},
#           "argument":   {"claim_presence": True, ...},
#           "readability": 7.0
#       }
#   }
#   result = new  (new completely replaces old since final_score key conflicts)
# -----------------------------------------------------------------------------

def merge_final_evaluation(old: dict | None, new: dict | None) -> dict:
    if old is None:
        return new
    if new is None:
        return old
    return {**old, **new}
