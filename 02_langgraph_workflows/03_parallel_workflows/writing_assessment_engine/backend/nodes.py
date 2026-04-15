# =============================================================================
# nodes.py — All pipeline nodes for the Parallel Writing Assessment Engine
#
# This file defines EVERY function that LangGraph calls as a node.
# There are 11 nodes total, grouped into 5 stages:
#
#   STAGE 1 — Format Detection (1 node, no LLM)
#     format_classifier_node        → detects "paragraph", "essay", "article"
#
#   STAGE 2 — Parallel LLM Scoring (8 nodes, run simultaneously)
#     grammar_evaluator_node        → scores grammar correctness
#     clarity_evaluator_node        → scores clarity of expression
#     coherence_evaluator_node      → scores logical flow between ideas
#     depth_evaluator_node          → scores thoroughness of topic exploration
#     structure_evaluator_node      → scores organizational layout
#     vocabulary_evaluator_node     → scores word choice and variety
#     tone_evaluator_node           → scores formality and audience fit
#     readability_evaluator_node    → scores reading ease and pacing
#
#   STAGE 3 — Argument Analysis (1 node, runs in parallel with stage 2)
#     argument_structure_node       → evaluates 5 argument-quality dimensions
#
#   STAGE 4 — Score Merging (1 node, no LLM, runs after all parallel nodes)
#     evaluation_merger_node        → groups scores, computes final_score
#
#   STAGE 5 — Feedback Generation (1 node, LLM, runs last)
#     feedback_generator_node       → generates structured improvement report
#
# =============================================================================
#
# HOW EACH EVALUATOR NODE WORKS (same pattern for all 8):
#
#   1. Call get_llm() to create a fresh Claude instance
#   2. Attach with_structured_output(ScoreOutput) — forces Claude to respond
#      via tool calling, guaranteeing a Pydantic ScoreOutput object back
#   3. Call .invoke(prompt_fn(state["text"])) — sends the prompt to Claude
#   4. Return {"score_field": result.score} — only the field this node owns
#
#   LangGraph merges this return dict into the shared WritingState using the
#   reducer attached to that field in state.py (Annotated[float, _take_new]).
#
# =============================================================================
#
# IMPORTS:
#   state.py    → WritingState (type hint for all node arguments)
#   config.py   → SCORE_WEIGHTS (used in evaluation_merger_node)
#   llm.py      → get_llm() (creates ChatAnthropic instance)
#   prompts.py  → one prompt function per evaluator node
#   schemas.py  → ScoreOutput, ArgumentOutput, FeedbackOutput
#   router.py   → classify_format() (used in format_classifier_node)
#   reducers.py → merge_* functions (used in evaluation_merger_node)
# =============================================================================

from typing   import cast
from state    import WritingState
from config   import SCORE_WEIGHTS
from llm      import get_llm
from prompts  import (
    grammar_prompt,
    clarity_prompt,
    coherence_prompt,
    depth_prompt,
    structure_prompt,
    vocabulary_prompt,
    tone_prompt,
    readability_prompt,
    argument_prompt,
    feedback_prompt,
)
from schemas  import ScoreOutput, ArgumentOutput, FeedbackOutput
from router   import classify_format
from reducers import (
    merge_language_scores,
    merge_argument_scores,
    merge_structure_scores,
    merge_final_evaluation,
)


# =============================================================================
# STAGE 1 — FORMAT CLASSIFIER NODE
# =============================================================================

def format_classifier_node(state: WritingState) -> dict:
    """
    Detect the format of the submitted writing.

    This is the FIRST node in the graph. It runs before any LLM call.
    It uses keyword scoring + word count logic from router.py to classify
    the text into one of: "paragraph", "essay", "article".

    Why no LLM here?
        Format detection is deterministic — we use a scoring heuristic.
        Using an LLM just to produce a single label adds unnecessary cost
        and latency to every request. Keyword rules are fast, free, and reliable.

    Args:
        state (WritingState): the full graph state.
                              We only read state["text"] here.

    Returns:
        dict: {"format_type": "essay"}  (or "paragraph" or "article")
              LangGraph merges this into WritingState["format_type"]
    """

    # classify_format() returns "paragraph", "essay", or "article"
    # based on keyword scoring + word count guard (see router.py for details)
    detected_format = classify_format(state["text"])

    # Return only the field this node is responsible for writing
    return {"format_type": detected_format}


# =============================================================================
# STAGE 2 — PARALLEL EVALUATOR NODES (8 nodes)
#
# All 8 nodes follow EXACTLY the same pattern:
#
#   structured_llm = get_llm().with_structured_output(ScoreOutput)
#   result: ScoreOutput = structured_llm.invoke(prompt_fn(state["text"]))
#   return {score_field: result.score}
#
# with_structured_output(ScoreOutput) forces Claude to respond via tool calling.
# Claude physically cannot return free text — it MUST fill in score + reason.
# The result is a typed Python object (ScoreOutput), not a raw JSON string.
# =============================================================================

def grammar_evaluator_node(state: WritingState) -> dict:
    """
    Score the grammatical correctness of the submitted text.

    Evaluates: spelling, punctuation, subject-verb agreement, tense consistency,
    sentence fragments, run-on sentences.

    Args:
        state (WritingState): reads state["text"]

    Returns:
        dict: {"grammar_score": float}  — a score between 0.0 and 10.0
    """

    # Step 1: Create a Claude LLM instance and bind it to ScoreOutput schema.
    #         with_structured_output uses Claude's tool-calling feature to force
    #         Claude to return { score: float, reason: str } — guaranteed structure.
    structured_llm = get_llm().with_structured_output(ScoreOutput)

    # Step 2: Send the grammar-specific prompt to Claude.
    #         grammar_prompt(text) returns a formatted string with the text
    #         embedded inside and a clear evaluation instruction for Claude.
    result = cast(ScoreOutput, structured_llm.invoke(grammar_prompt(state["text"])))

    # Step 3: Return only the grammar_score field.
    #         result.score is a float (e.g. 7.5) — already validated by Pydantic.
    #         result.reason is available but we don't store it in state.
    return {"grammar_score": result.score}


def clarity_evaluator_node(state: WritingState) -> dict:
    """
    Score how clearly the text communicates its ideas.

    Evaluates: sentence complexity, use of jargon, ambiguous phrasing,
    directness, ease of understanding on first read.

    Args:
        state (WritingState): reads state["text"]

    Returns:
        dict: {"clarity_score": float}
    """

    # Same 3-step pattern as grammar_evaluator_node:
    # bind schema → invoke with prompt → return the score field
    structured_llm = get_llm().with_structured_output(ScoreOutput)
    result = cast(ScoreOutput, structured_llm.invoke(clarity_prompt(state["text"])))
    return {"clarity_score": result.score}


def coherence_evaluator_node(state: WritingState) -> dict:
    """
    Score how well ideas connect and flow throughout the text.

    Evaluates: logical progression, transition words, paragraph linking,
    consistency of topic, absence of abrupt topic shifts.

    Args:
        state (WritingState): reads state["text"]

    Returns:
        dict: {"coherence_score": float}
    """

    structured_llm = get_llm().with_structured_output(ScoreOutput)
    result = cast(ScoreOutput, structured_llm.invoke(coherence_prompt(state["text"])))
    return {"coherence_score": result.score}


def depth_evaluator_node(state: WritingState) -> dict:
    """
    Score how thoroughly the text explores its topic.

    Evaluates: use of specific examples, supporting details, complexity of ideas,
    nuance, evidence of research or independent thinking.

    Args:
        state (WritingState): reads state["text"]

    Returns:
        dict: {"depth_score": float}
    """

    structured_llm = get_llm().with_structured_output(ScoreOutput)
    result = cast(ScoreOutput, structured_llm.invoke(depth_prompt(state["text"])))
    return {"depth_score": result.score}


def structure_evaluator_node(state: WritingState) -> dict:
    """
    Score the organizational structure of the text.

    Evaluates: presence of introduction, body, and conclusion, logical ordering
    of sections, paragraph organization, whether structure serves the content.

    Args:
        state (WritingState): reads state["text"]

    Returns:
        dict: {"structure_score": float}
    """

    structured_llm = get_llm().with_structured_output(ScoreOutput)
    result = cast(ScoreOutput, structured_llm.invoke(structure_prompt(state["text"])))
    return {"structure_score": result.score}


def vocabulary_evaluator_node(state: WritingState) -> dict:
    """
    Score the vocabulary used in the text.

    Evaluates: word variety, richness of expression, avoidance of repetition,
    appropriateness for the format and audience, use of precise language.

    Args:
        state (WritingState): reads state["text"]

    Returns:
        dict: {"vocabulary_score": float}
    """

    structured_llm = get_llm().with_structured_output(ScoreOutput)
    result = cast(ScoreOutput, structured_llm.invoke(vocabulary_prompt(state["text"])))
    return {"vocabulary_score": result.score}


def tone_evaluator_node(state: WritingState) -> dict:
    """
    Score the tone and voice consistency of the text.

    Evaluates: consistency of voice, formality level, audience alignment,
    unexpected tone shifts, whether tone matches the writing's purpose.

    Args:
        state (WritingState): reads state["text"]

    Returns:
        dict: {"tone_score": float}
    """

    structured_llm = get_llm().with_structured_output(ScoreOutput)
    result = cast(ScoreOutput, structured_llm.invoke(tone_prompt(state["text"])))
    return {"tone_score": result.score}


def readability_evaluator_node(state: WritingState) -> dict:
    """
    Score how readable and effortless the text is to read.

    Evaluates: sentence length variation, overuse of passive voice, lexical
    density (content words / total words), paragraph length, overall reading ease.

    Args:
        state (WritingState): reads state["text"]

    Returns:
        dict: {"readability_score": float}
    """

    structured_llm = get_llm().with_structured_output(ScoreOutput)
    result = cast(ScoreOutput, structured_llm.invoke(readability_prompt(state["text"])))
    return {"readability_score": result.score}


# =============================================================================
# STAGE 3 — ARGUMENT STRUCTURE NODE
#
# Runs in PARALLEL with the 8 evaluator nodes above.
# Unlike evaluator nodes, this one uses ArgumentOutput instead of ScoreOutput.
# ArgumentOutput has 5 fields instead of 1 score — see schemas.py for details.
# =============================================================================

def argument_structure_node(state: WritingState) -> dict:
    """
    Evaluate the argumentative quality of the text across 5 dimensions.

    This node runs in PARALLEL with all 8 evaluator nodes.
    It uses ArgumentOutput (not ScoreOutput) because it measures 5 categorical
    fields instead of a single numeric score.

    ArgumentOutput fields (from schemas.py):
        claim_presence          — bool:  is there a clear central claim?
        supporting_evidence     — str:   "none" | "weak" | "moderate" | "strong"
        reasoning_quality       — str:   "poor" | "fair" | "good" | "excellent"
        counterargument_usage   — bool:  does the text address opposing views?
        critical_thinking_depth — str:   "surface" | "moderate" | "deep"

    Args:
        state (WritingState): reads state["text"]

    Returns:
        dict: {"argument_analysis": {claim_presence, supporting_evidence, ...}}
              LangGraph merges this into state["argument_analysis"] using
              the _merge_dicts reducer defined in state.py.
    """

    # Bind Claude to ArgumentOutput schema — Claude must fill all 5 fields
    structured_llm = get_llm().with_structured_output(ArgumentOutput)

    # argument_prompt() gives Claude detailed instructions on all 5 dimensions
    result = cast(ArgumentOutput, structured_llm.invoke(argument_prompt(state["text"])))

    # Convert the Pydantic object to a plain dict before writing to state.
    # LangGraph state values must be JSON-serializable standard Python types.
    # model_dump() converts the Pydantic model to a dict automatically.
    return {
        "argument_analysis": result.model_dump()
        # result.model_dump() produces:
        # {
        #     "claim_presence": True,
        #     "supporting_evidence": "moderate",
        #     "reasoning_quality": "good",
        #     "counterargument_usage": False,
        #     "critical_thinking_depth": "moderate"
        # }
    }


# =============================================================================
# STAGE 4 — EVALUATION MERGER NODE
#
# Runs AFTER all 8 evaluator nodes AND argument_structure_node have finished.
# LangGraph waits for all parallel branches to complete before calling this node.
#
# This node does 3 things (no LLM involved):
#   1. Pull all 8 individual scores from state
#   2. Group them into dimension_breakdown using reducers from reducers.py
#   3. Compute the weighted final_score using SCORE_WEIGHTS from config.py
# =============================================================================

def evaluation_merger_node(state: WritingState) -> dict:
    """
    Combine all 8 dimension scores and argument analysis into a grouped summary.
    Compute the weighted final score.

    This node runs AFTER all parallel evaluator nodes complete.
    LangGraph guarantees that by the time this node runs, all 8 score fields
    in WritingState have been populated.

    Returns:
        dict: {
            "dimension_breakdown": {
                "language":     {"grammar": x, "clarity": x, "vocabulary": x, "tone": x},
                "structure":    {"structure": x, "coherence": x, "depth": x},
                "argument":     {claim_presence, supporting_evidence, ...},
                "readability":  float
            },
            "final_score": float   (weighted average, 0.0 to 10.0)
        }
    """

    # -------------------------------------------------------------------------
    # STEP 1 — Collect all individual scores from the shared state.
    # By the time this node runs, all 8 parallel nodes have written their scores.
    # -------------------------------------------------------------------------

    grammar_score     = state["grammar_score"]
    clarity_score     = state["clarity_score"]
    coherence_score   = state["coherence_score"]
    depth_score       = state["depth_score"]
    structure_score   = state["structure_score"]
    vocabulary_score  = state["vocabulary_score"]
    tone_score        = state["tone_score"]
    readability_score = state["readability_score"]
    argument_analysis = state["argument_analysis"]

    # -------------------------------------------------------------------------
    # STEP 2 — Group scores into dimension categories using reducers.
    #
    # Why call reducers manually here instead of letting LangGraph handle it?
    #   The reducers in reducers.py are for GROUPING scores by category —
    #   that's a logical operation we do here, not a conflict-resolution
    #   operation LangGraph needs to know about.
    #
    #   The reducers in state.py (Annotated fields) are for CONCURRENT WRITE
    #   safety during parallel execution.
    #
    #   These are different levels of merging.
    # -------------------------------------------------------------------------

    # Language group: grammar, clarity, vocabulary, tone
    # These all measure HOW the writer uses language
    language_group = merge_language_scores(
        old=None,   # no previous state — building fresh
        new={
            "grammar":    grammar_score,
            "clarity":    clarity_score,
            "vocabulary": vocabulary_score,
            "tone":       tone_score,
        }
    )

    # Structure group: structure, coherence, depth
    # These measure HOW the writing is organized and developed
    structure_group = merge_structure_scores(
        old=None,
        new={
            "structure":  structure_score,
            "coherence":  coherence_score,
            "depth":      depth_score,
        }
    )

    # Argument group: the 5-field dict from argument_structure_node
    # Stored directly — no additional scoring to compute
    argument_group = merge_argument_scores(
        old=None,
        new=argument_analysis  # already a dict from argument_structure_node
    )

    # -------------------------------------------------------------------------
    # STEP 3 — Build the dimension_breakdown dict.
    # This becomes the "dimension_scores" field in the API response.
    # -------------------------------------------------------------------------

    dimension_breakdown = {
        "language":    language_group,
        "structure":   structure_group,
        "argument":    argument_group,
        "readability": readability_score,   # single float, not a group
    }

    # -------------------------------------------------------------------------
    # STEP 4 — Compute the weighted final_score.
    #
    # SCORE_WEIGHTS from config.py:
    #   grammar: 0.15, clarity: 0.15, coherence: 0.15, depth: 0.10,
    #   structure: 0.10, vocabulary: 0.10, tone: 0.10, readability: 0.15
    # All weights sum to 1.0 exactly.
    #
    # Formula:
    #   final_score = (grammar * 0.15) + (clarity * 0.15) + (coherence * 0.15)
    #               + (depth * 0.10) + (structure * 0.10) + (vocabulary * 0.10)
    #               + (tone * 0.10) + (readability * 0.15)
    # -------------------------------------------------------------------------

    # Map dimension names to their score values
    score_map = {
        "grammar":     grammar_score,
        "clarity":     clarity_score,
        "coherence":   coherence_score,
        "depth":       depth_score,
        "structure":   structure_score,
        "vocabulary":  vocabulary_score,
        "tone":        tone_score,
        "readability": readability_score,
    }

    # Weighted sum: multiply each score by its weight and sum all products
    final_score = sum(
        score_map[dim] * weight
        for dim, weight in SCORE_WEIGHTS.items()
    )

    # Round to 2 decimal places for clean display in the API response
    final_score = round(final_score, 2)

    # -------------------------------------------------------------------------
    # STEP 5 — Return the merged evaluation back to WritingState.
    # LangGraph writes these into the shared state fields:
    #   dimension_breakdown → merged via _merge_dicts reducer (state.py)
    #   final_score         → overwritten via _take_new reducer (state.py)
    # -------------------------------------------------------------------------

    return merge_final_evaluation(
        old=None,
        new={
            "dimension_breakdown": dimension_breakdown,
            "final_score": final_score,
        }
    )


# =============================================================================
# STAGE 5 — FEEDBACK GENERATOR NODE
#
# The LAST node in the graph. Runs after evaluation_merger_node completes.
# Uses FeedbackOutput schema (5 list fields + 1 string) — see schemas.py.
#
# This is the most expensive LLM call because feedback_prompt() passes:
#   - All 8 dimension scores (as a formatted summary)
#   - The format type ("paragraph", "essay", "article")
#   - The full original text
# Claude uses all three to generate text-specific, score-aware feedback.
# =============================================================================

def feedback_generator_node(state: WritingState) -> dict:
    """
    Generate structured writing improvement feedback using all dimension scores.

    This is the FINAL node in the pipeline. It receives the fully populated
    state — all scores computed, format detected — and asks Claude to produce
    a structured improvement report.

    FeedbackOutput fields (from schemas.py):
        strengths                    — List[str]: 3 specific writing strengths
        weaknesses                   — List[str]: 3 specific areas to improve
        revision_plan                — List[str]: 3 actionable revision steps
        recommended_style_adjustments — List[str]: 2 style changes to make
        target_band_prediction       — str: "Band X-Y: <one-sentence justification>"

    Args:
        state (WritingState): reads format_type, all 8 scores, and text

    Returns:
        dict: {"feedback_report": {strengths, weaknesses, revision_plan, ...}}
              LangGraph merges this into state["feedback_report"] using
              the _merge_dicts reducer defined in state.py.
    """

    # -------------------------------------------------------------------------
    # STEP 1 — Collect the scores that feedback_prompt() needs.
    # feedback_prompt() accepts a flat dict of {dimension: score} pairs.
    # -------------------------------------------------------------------------

    scores = {
        "grammar":     state["grammar_score"],
        "clarity":     state["clarity_score"],
        "coherence":   state["coherence_score"],
        "depth":       state["depth_score"],
        "structure":   state["structure_score"],
        "vocabulary":  state["vocabulary_score"],
        "tone":        state["tone_score"],
        "readability": state["readability_score"],
    }

    # -------------------------------------------------------------------------
    # STEP 2 — Bind Claude to FeedbackOutput and invoke with the feedback prompt.
    #
    # feedback_prompt(scores, format_type, text) builds a prompt that shows Claude:
    #   - A formatted score breakdown (e.g. "Grammar: 7.5/10")
    #   - The format type ("This is an essay...")
    #   - The full original text
    #
    # Claude then fills in all 5 FeedbackOutput fields via tool calling.
    # -------------------------------------------------------------------------

    structured_llm = get_llm().with_structured_output(FeedbackOutput)

    result = cast(FeedbackOutput, structured_llm.invoke(
        feedback_prompt(
            scores=scores,
            format_type=state["format_type"],
            text=state["text"],
        )
    ))

    # -------------------------------------------------------------------------
    # STEP 3 — Convert FeedbackOutput Pydantic model to a plain dict.
    # model_dump() serializes all 5 fields to a standard Python dict.
    # This is what gets written to state["feedback_report"].
    # -------------------------------------------------------------------------

    return {
        "feedback_report": result.model_dump()
        # result.model_dump() produces:
        # {
        #     "strengths": ["...", "...", "..."],
        #     "weaknesses": ["...", "...", "..."],
        #     "revision_plan": ["...", "...", "..."],
        #     "recommended_style_adjustments": ["...", "..."],
        #     "target_band_prediction": "Band 7-8: ..."
        # }
    }
