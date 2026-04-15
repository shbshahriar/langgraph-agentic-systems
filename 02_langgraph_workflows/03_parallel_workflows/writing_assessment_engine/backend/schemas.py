# =============================================================================
# schemas.py — Pydantic models for the Writing Assessment Engine
#
# TWO categories of schemas live here:
#
# ── CATEGORY 1: LLM OUTPUT SCHEMAS ──────────────────────────────────────────
#   Used with llm.with_structured_output(Schema) in nodes.py.
#   LangChain converts these Pydantic models into Claude tool definitions.
#   Claude is forced to respond via tool calling — guaranteed structured output.
#   No JSON parsing needed in nodes.py — result is already a typed Python object.
#
#   ScoreOutput    → returned by all 8 parallel evaluator nodes
#   ArgumentOutput → returned by argument_structure_node
#   FeedbackOutput → returned by feedback_generator_node
#
# ── CATEGORY 2: API SCHEMAS ──────────────────────────────────────────────────
#   Used by FastAPI in app.py to validate incoming requests and shape responses.
#   FastAPI automatically generates /docs (Swagger UI) from these models.
#
#   WritingRequest  → validates POST /evaluate-writing request body
#   WritingResponse → shapes the JSON response returned to the frontend
#
# IMPORT ORDER IN OTHER FILES:
#   nodes.py   imports → ScoreOutput, ArgumentOutput, FeedbackOutput
#   app.py     imports → WritingRequest, WritingResponse
# =============================================================================

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


# =============================================================================
# CATEGORY 1 — LLM OUTPUT SCHEMAS
# These are passed to llm.with_structured_output() in nodes.py.
# Field descriptions are important — LangChain includes them in the tool
# definition sent to Claude, so Claude understands exactly what to return.
# =============================================================================


class ScoreOutput(BaseModel):
    """
    Output schema for all 8 parallel evaluator nodes:
        grammar_evaluator_node
        clarity_evaluator_node
        coherence_evaluator_node
        depth_evaluator_node
        structure_evaluator_node
        vocabulary_evaluator_node
        tone_evaluator_node
        readability_evaluator_node

    Usage in nodes.py:
        structured_llm = llm.with_structured_output(ScoreOutput)
        result: ScoreOutput = structured_llm.invoke(grammar_prompt(text))
        score = result.score    # guaranteed float 0–10
        reason = result.reason  # guaranteed string
    """

    score: float = Field(
        description=(
            "A score between 0.0 and 10.0 reflecting the quality of the evaluated dimension. "
            "0–3 = poor, 4–5 = below average, 6–7 = average, 8–9 = good, 10 = excellent."
        )
    )

    reason: str = Field(
        description=(
            "One sentence explaining why this score was given. "
            "Be specific — mention a concrete feature of the text."
        )
    )


class ArgumentOutput(BaseModel):
    """
    Output schema for argument_structure_node.
    Evaluates 5 dimensions of argumentative quality instead of a single score.

    Usage in nodes.py:
        structured_llm = llm.with_structured_output(ArgumentOutput)
        result: ArgumentOutput = structured_llm.invoke(argument_prompt(text))
        result.claim_presence          # bool
        result.supporting_evidence     # "none" | "weak" | "moderate" | "strong"
        result.reasoning_quality       # "poor" | "fair" | "good" | "excellent"
        result.counterargument_usage   # bool
        result.critical_thinking_depth # "surface" | "moderate" | "deep"
    """

    claim_presence: bool = Field(
        description=(
            "True if the text makes a clear central claim, thesis, or main argument. "
            "False if the text lacks a discernible central point."
        )
    )

    supporting_evidence: str = Field(
        description=(
            "Quality of evidence used to support claims. "
            "Must be one of: 'none', 'weak', 'moderate', 'strong'."
        )
    )

    reasoning_quality: str = Field(
        description=(
            "Quality of the logical reasoning connecting claims to evidence. "
            "Must be one of: 'poor', 'fair', 'good', 'excellent'."
        )
    )

    counterargument_usage: bool = Field(
        description=(
            "True if the text acknowledges, addresses, or refutes opposing viewpoints. "
            "False if it presents only one side without recognizing alternatives."
        )
    )

    critical_thinking_depth: str = Field(
        description=(
            "Depth of analytical thinking demonstrated in the text. "
            "Must be one of: 'surface', 'moderate', 'deep'."
        )
    )


class FeedbackOutput(BaseModel):
    """
    Output schema for feedback_generator_node.
    Produces a structured writing improvement report based on all dimension scores.

    Usage in nodes.py:
        structured_llm = llm.with_structured_output(FeedbackOutput)
        result: FeedbackOutput = structured_llm.invoke(feedback_prompt(scores, format_type, text))
        result.strengths                     # List[str]
        result.weaknesses                    # List[str]
        result.revision_plan                 # List[str]
        result.recommended_style_adjustments # List[str]
        result.target_band_prediction        # str
    """

    strengths: List[str] = Field(
        description=(
            "A list of 3 specific strengths observed in the writing. "
            "Each item should reference a concrete feature or pattern from the text."
        )
    )

    weaknesses: List[str] = Field(
        description=(
            "A list of 3 specific weaknesses or areas needing improvement. "
            "Each item should be honest and constructive, referencing actual issues in the text."
        )
    )

    revision_plan: List[str] = Field(
        description=(
            "A list of 3 concrete, actionable revision steps the writer can follow. "
            "Each step should directly address one of the identified weaknesses."
        )
    )

    recommended_style_adjustments: List[str] = Field(
        description=(
            "A list of 2 specific style changes that would improve the writing. "
            "Examples: vary sentence length, reduce passive voice, use stronger verbs."
        )
    )

    target_band_prediction: str = Field(
        description=(
            "A predicted score band based on the dimension scores. "
            "Format: 'Band X–Y: <one sentence justification>'. "
            "Example: 'Band 7–8: The writing demonstrates strong clarity and grammar "
            "but lacks depth in supporting arguments.'"
        )
    )


# =============================================================================
# CATEGORY 2 — API SCHEMAS
# Used by FastAPI in app.py.
# FastAPI reads these models to:
#   1. Validate and parse incoming request bodies automatically
#   2. Serialize response objects to JSON automatically
#   3. Generate interactive /docs (Swagger UI) for testing
# =============================================================================


class WritingRequest(BaseModel):
    """
    Request body for POST /evaluate-writing.

    The frontend sends a JSON body with a single field: the text to evaluate.
    FastAPI validates that 'text' is present and is a non-empty string.

    Example request body:
        {
            "text": "Climate change is one of the most pressing issues..."
        }
    """

    text: str = Field(
        min_length=10,
        description=(
            "The writing to evaluate. Must be at least 10 characters. "
            "Supported formats: paragraph, essay, article."
        )
    )


class WritingResponse(BaseModel):
    """
    Response body for POST /evaluate-writing.

    Returned to the frontend after the full LangGraph pipeline completes.
    Maps directly to the fields in WritingState that the nodes populate.

    Example response:
        {
            "format_type": "essay",
            "dimension_scores": {
                "language":  {"grammar": 7.5, "clarity": 8.0, ...},
                "structure": {"structure": 8.0, "coherence": 7.5, ...},
                "argument":  {"claim_presence": true, ...},
                "readability": 7.0
            },
            "argument_analysis": {
                "claim_presence": true,
                "supporting_evidence": "moderate",
                ...
            },
            "final_score": 7.6,
            "feedback_report": {
                "strengths": [...],
                "weaknesses": [...],
                "revision_plan": [...],
                "recommended_style_adjustments": [...],
                "target_band_prediction": "Band 7–8: ..."
            }
        }
    """

    format_type: str = Field(
        description="Detected writing format: 'paragraph', 'essay', or 'article'."
    )

    dimension_scores: dict = Field(
        description=(
            "Grouped breakdown of all dimension scores. "
            "Keys: 'language', 'structure', 'argument', 'readability'. "
            "Built by evaluation_merger_node from all 8 parallel evaluator outputs."
        )
    )

    argument_analysis: dict = Field(
        description=(
            "Full argument structure analysis from argument_structure_node. "
            "Keys: claim_presence, supporting_evidence, reasoning_quality, "
            "counterargument_usage, critical_thinking_depth."
        )
    )

    final_score: float = Field(
        description=(
            "Weighted average of all 8 dimension scores. Range: 0.0–10.0. "
            "Computed by evaluation_merger_node using SCORE_WEIGHTS from config.py."
        )
    )

    feedback_report: dict = Field(
        description=(
            "Structured improvement report from feedback_generator_node. "
            "Keys: strengths, weaknesses, revision_plan, "
            "recommended_style_adjustments, target_band_prediction."
        )
    )

    error: Optional[str] = Field(
        default=None,
        description=(
            "Error message if the pipeline failed. None on success. "
            "Included so the frontend can display a user-friendly error."
        )
    )
