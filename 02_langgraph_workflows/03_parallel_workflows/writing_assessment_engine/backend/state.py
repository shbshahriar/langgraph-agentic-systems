# =============================================================================
# state.py — Shared state definition for the Parallel Writing Assessment Engine
#
# WritingState is a TypedDict that acts as the single shared "data bucket"
# flowing through every node in the LangGraph graph.
#
# WHY TypedDict?
#   LangGraph requires state to be a TypedDict (or dataclass).
#   It gives Python type hints so your IDE can catch mistakes early,
#   and it tells LangGraph exactly what fields exist in the state.
#
# WHY Annotated + reducer?
#   In a parallel graph, multiple nodes run AT THE SAME TIME and all try
#   to write back to the same state object. Without a reducer, the last
#   write would overwrite all others — losing data.
#
#   Annotated[type, reducer_fn] tells LangGraph:
#     "when two nodes both update this field, call reducer_fn(old, new)
#      to merge them instead of overwriting"
#
#   Example:
#     grammar_evaluator_node  writes → grammar_score = 7.5
#     clarity_evaluator_node  writes → clarity_score = 8.0
#     Both run in parallel. Without reducers, one would overwrite the other.
#     With reducers, both values are safely merged into the state.
# =============================================================================

from __future__ import annotations

from typing import Annotated, Any
from typing_extensions import TypedDict


# -----------------------------------------------------------------------------
# REDUCER FUNCTIONS
# These are tiny merge functions defined inline here because they are
# only used by the Annotated fields below. They tell LangGraph how to
# combine the old value and the new value when parallel nodes both write
# to the same field.
#
# For simple numeric scores:  always take the new value (the node just computed it)
# For dicts (argument_analysis, feedback_report): merge keys so no data is lost
# -----------------------------------------------------------------------------

def _take_new(__: Any, new: Any) -> Any:
    """
    Reducer for scalar fields (float scores, strings).
    Simply returns the new value — the node that just ran computed it fresh.
    We use this instead of letting LangGraph use a default (which would error
    on concurrent writes without a reducer).
    """
    return new


def _merge_dicts(old: dict, new: dict) -> dict:
    """
    Reducer for dictionary fields (argument_analysis, feedback_report).
    Merges old and new dicts together so no keys are lost.
    If both have the same key, the new value wins.

    Example:
        old = {"claim_presence": True}
        new = {"reasoning_quality": "strong"}
        result = {"claim_presence": True, "reasoning_quality": "strong"}
    """
    if old is None:
        return new
    if new is None:
        return old
    return {**old, **new}


# =============================================================================
# WritingState
#
# This TypedDict defines every field that exists in the graph's shared state.
# Nodes read fields they need and return only the fields they update.
# LangGraph merges each returned field back into the state using the reducer.
#
# FIELD GROUPS:
#
#   [INPUT]
#     text         — the raw writing submitted by the user
#     format_type  — detected by format_classifier_node ("paragraph"/"essay"/"article")
#
#   [PARALLEL SCORES — written by 8 evaluator nodes running simultaneously]
#     grammar_score      — grammatical correctness (0–10)
#     clarity_score      — ease of understanding (0–10)
#     coherence_score    — logical flow between ideas (0–10)
#     depth_score        — thoroughness of exploration (0–10)
#     structure_score    — organization and layout (0–10)
#     vocabulary_score   — word choice and variety (0–10)
#     tone_score         — formality and audience fit (0–10)
#     readability_score  — sentence complexity and reading ease (0–10)
#
#   [ARGUMENT ANALYSIS — written by argument_structure_node]
#     argument_analysis  — dict with keys: claim_presence, supporting_evidence,
#                          reasoning_quality, counterargument_usage,
#                          critical_thinking_depth
#
#   [FINAL OUTPUT — written sequentially after all parallel nodes finish]
#     final_score      — weighted average of all 8 dimension scores
#     feedback_report  — LLM-generated dict with strengths, weaknesses,
#                        revision_plan, recommended_style_adjustments,
#                        target_band_prediction
# =============================================================================

class WritingState(TypedDict):

    # -------------------------------------------------------------------------
    # INPUT FIELDS
    # Set once at the start by the API layer before the graph runs.
    # No parallel writes happen here — no reducer needed.
    # -------------------------------------------------------------------------

    text: str
    # The raw writing text submitted by the user via POST /evaluate-writing.
    # All evaluator nodes read this field to score the content.

    format_type: str
    # Detected format: "paragraph", "essay", or "article".
    # Set by format_classifier_node using router.py logic.
    # Used by feedback_generator_node to tailor its suggestions.

    # -------------------------------------------------------------------------
    # PARALLEL SCORE FIELDS
    # Each of these is written by a separate evaluator node.
    # All 8 nodes run at the same time (in parallel) after format_classifier.
    # Annotated + _take_new reducer ensures safe concurrent writes.
    #
    # Default value is 0.0 — if a node fails or is skipped, score stays 0.
    # -------------------------------------------------------------------------

    grammar_score: Annotated[float, _take_new]
    # Written by: grammar_evaluator_node
    # Measures: sentence correctness, punctuation, spelling errors

    clarity_score: Annotated[float, _take_new]
    # Written by: clarity_evaluator_node
    # Measures: how easy the text is to understand on first read

    coherence_score: Annotated[float, _take_new]
    # Written by: coherence_evaluator_node
    # Measures: logical flow, smooth transitions between ideas and paragraphs

    depth_score: Annotated[float, _take_new]
    # Written by: depth_evaluator_node
    # Measures: how thoroughly the topic is explored, use of examples and evidence

    structure_score: Annotated[float, _take_new]
    # Written by: structure_evaluator_node
    # Measures: overall organization — intro, body, conclusion present and logical

    vocabulary_score: Annotated[float, _take_new]
    # Written by: vocabulary_evaluator_node
    # Measures: word variety, avoidance of repetition, appropriateness for format

    tone_score: Annotated[float, _take_new]
    # Written by: tone_evaluator_node
    # Measures: formality level, consistency of voice, audience alignment

    readability_score: Annotated[float, _take_new]
    # Written by: readability_evaluator_node
    # Measures: sentence length variation, passive voice usage, lexical density

    # -------------------------------------------------------------------------
    # ARGUMENT ANALYSIS FIELD
    # Written by argument_structure_node (runs in parallel with other evaluators).
    # Returns a dictionary instead of a float — uses _merge_dicts reducer
    # so individual keys from separate writes are never lost.
    # -------------------------------------------------------------------------

    argument_analysis: Annotated[dict, _merge_dicts]
    # Written by: argument_structure_node
    # Keys produced:
    #   claim_presence         — bool: does the text make a clear claim?
    #   supporting_evidence    — str:  quality of evidence used
    #   reasoning_quality      — str:  how well arguments are reasoned
    #   counterargument_usage  — bool: does it acknowledge opposing views?
    #   critical_thinking_depth — str: depth of analytical thinking shown

    # -------------------------------------------------------------------------
    # FINAL OUTPUT FIELDS
    # Written sequentially AFTER all parallel nodes have completed.
    # evaluation_merger_node writes final_score.
    # feedback_generator_node writes feedback_report.
    # No parallel conflict here — _take_new is still used for safety.
    # -------------------------------------------------------------------------

    dimension_breakdown: Annotated[dict, _merge_dicts]
    # Written by: evaluation_merger_node
    # A grouped summary of all scores, structured for the API response.
    # Keys produced:
    #   language  — {"grammar": x, "clarity": x, "vocabulary": x, "tone": x}
    #   structure — {"structure": x, "coherence": x, "depth": x}
    #   argument  — full argument_analysis dict (claim, evidence, reasoning, ...)
    #   readability — float score
    # This maps to "dimension_scores" in the API response (POST /evaluate-writing).

    final_score: Annotated[float, _take_new]
    # Written by: evaluation_merger_node
    # Formula: sum(score[dim] * SCORE_WEIGHTS[dim] for dim in SCORE_WEIGHTS)
    # Range: 0.0 – 10.0

    feedback_report: Annotated[dict, _merge_dicts]
    # Written by: feedback_generator_node
    # Keys produced:
    #   strengths                    — list of what the writing does well
    #   weaknesses                   — list of areas needing improvement
    #   revision_plan                — step-by-step improvement suggestions
    #   recommended_style_adjustments — specific style changes to make
    #   target_band_prediction       — predicted score band (e.g. "Band 7–8")
