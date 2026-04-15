# =============================================================================
# prompts.py — Prompt builder functions for the Writing Assessment Engine
#
# This file has NO imports, NO LLM calls, NO logic beyond string formatting.
# Every function takes text (and optionally other data) and returns a prompt
# string ready to be sent to Claude via llm.with_structured_output().invoke().
#
# WHY SEPARATE PROMPTS FROM NODES?
#   nodes.py contains the execution logic (call LLM, parse response, update state).
#   prompts.py contains only the instruction text sent to the LLM.
#   Keeping them separate means:
#     - You can tune any prompt without touching node logic
#     - All prompts are in one file — easy to review, compare, and improve
#     - nodes.py stays short and readable
#
# WHY NO "RETURN ONLY JSON" INSTRUCTION?
#   We use llm.with_structured_output(PydanticModel) in nodes.py.
#   LangChain converts the Pydantic model into a tool definition and forces
#   Claude to respond via tool calling — which guarantees structured output.
#   Claude physically cannot return free text in this mode.
#   So we do NOT need to instruct Claude about JSON format in the prompt.
#
# SCORING GUIDANCE IN PROMPTS:
#   Each prompt includes a score scale so Claude applies scores consistently:
#     0–3  = poor
#     4–5  = below average
#     6–7  = average / acceptable
#     8–9  = good
#     10   = excellent / near perfect
# =============================================================================


def grammar_prompt(text: str) -> str:
    """
    Prompt for grammar_evaluator_node.
    Evaluates: sentence correctness, punctuation, spelling, subject-verb agreement.

    Args:
        text (str): the raw writing submitted by the user

    Returns:
        str: formatted prompt string ready for llm.with_structured_output().invoke()
    """
    return f"""You are an expert writing evaluator specializing in grammar assessment.

Evaluate the grammatical correctness of the following text.
Consider: spelling errors, punctuation mistakes, subject-verb agreement,
tense consistency, sentence fragments, run-on sentences.

Score scale:
  0–3  = frequent errors that seriously disrupt reading
  4–5  = noticeable errors but meaning is still clear
  6–7  = minor errors, generally correct
  8–9  = very few errors, almost flawless
  10   = perfect grammar throughout

Text to evaluate:
\"\"\"{text}\"\"\""""


def clarity_prompt(text: str) -> str:
    """
    Prompt for clarity_evaluator_node.
    Evaluates: how easily the reader understands the writing on first read.
    Considers: sentence complexity, ambiguity, word choice, idea expression.

    Args:
        text (str): the raw writing submitted by the user

    Returns:
        str: formatted prompt string ready for llm.with_structured_output().invoke()
    """
    return f"""You are an expert writing evaluator specializing in clarity assessment.

Evaluate how clearly the following text communicates its ideas.
Consider: sentence length and complexity, use of jargon, ambiguous phrasing,
directness of expression, ease of understanding on first read.

Score scale:
  0–3  = very difficult to understand, meaning often unclear
  4–5  = some passages are confusing or require re-reading
  6–7  = mostly clear with occasional ambiguity
  8–9  = clear and easy to follow throughout
  10   = exceptionally clear, every idea is instantly understood

Text to evaluate:
\"\"\"{text}\"\"\""""


def coherence_prompt(text: str) -> str:
    """
    Prompt for coherence_evaluator_node.
    Evaluates: logical flow between sentences and paragraphs, smooth transitions,
    consistent topic progression, absence of abrupt topic jumps.

    Args:
        text (str): the raw writing submitted by the user

    Returns:
        str: formatted prompt string ready for llm.with_structured_output().invoke()
    """
    return f"""You are an expert writing evaluator specializing in coherence assessment.

Evaluate how well the ideas in the following text connect and flow together.
Consider: logical progression of ideas, use of transition words, paragraph
linking, consistency of topic, absence of abrupt topic shifts.

Score scale:
  0–3  = ideas are disjointed, no logical flow
  4–5  = some connections but flow is often broken
  6–7  = mostly flows well with some weak transitions
  8–9  = ideas connect smoothly throughout
  10   = seamless flow, ideas build perfectly on each other

Text to evaluate:
\"\"\"{text}\"\"\""""


def depth_prompt(text: str) -> str:
    """
    Prompt for depth_evaluator_node.
    Evaluates: how thoroughly the topic is explored, use of examples,
    supporting detail, complexity of ideas presented.

    Args:
        text (str): the raw writing submitted by the user

    Returns:
        str: formatted prompt string ready for llm.with_structured_output().invoke()
    """
    return f"""You are an expert writing evaluator specializing in content depth assessment.

Evaluate how thoroughly the following text explores its topic.
Consider: use of specific examples, supporting details, complexity of ideas,
nuance, avoidance of surface-level treatment, evidence of research or thought.

Score scale:
  0–3  = extremely shallow, only states obvious points
  4–5  = some detail but topic is underdeveloped
  6–7  = adequate depth with reasonable examples
  8–9  = thorough exploration with strong supporting detail
  10   = exceptional depth, nuanced and comprehensive coverage

Text to evaluate:
\"\"\"{text}\"\"\""""


def structure_prompt(text: str) -> str:
    """
    Prompt for structure_evaluator_node.
    Evaluates: overall organizational logic — whether the writing has a
    clear introduction, body, and conclusion, and whether sections are ordered.

    Args:
        text (str): the raw writing submitted by the user

    Returns:
        str: formatted prompt string ready for llm.with_structured_output().invoke()
    """
    return f"""You are an expert writing evaluator specializing in structural assessment.

Evaluate the organizational structure of the following text.
Consider: presence of introduction, body, and conclusion, logical ordering
of sections, paragraph organization, use of headings if appropriate,
whether the structure supports the content.

Score scale:
  0–3  = no discernible structure, chaotic organization
  4–5  = partial structure but sections are missing or misplaced
  6–7  = adequate structure with minor organizational issues
  8–9  = well-structured with clear and logical organization
  10   = perfectly structured, every section serves a clear purpose

Text to evaluate:
\"\"\"{text}\"\"\""""


def vocabulary_prompt(text: str) -> str:
    """
    Prompt for vocabulary_evaluator_node.
    Evaluates: word variety, richness, appropriateness for the format,
    avoidance of repetition, use of precise language.

    Args:
        text (str): the raw writing submitted by the user

    Returns:
        str: formatted prompt string ready for llm.with_structured_output().invoke()
    """
    return f"""You are an expert writing evaluator specializing in vocabulary assessment.

Evaluate the vocabulary used in the following text.
Consider: word variety, richness of expression, avoidance of repetition,
appropriateness of word choice for the format and audience,
use of precise and specific language over vague terms.

Score scale:
  0–3  = very limited vocabulary, heavy repetition
  4–5  = basic vocabulary, some variety
  6–7  = adequate vocabulary with reasonable range
  8–9  = rich and varied vocabulary, well-chosen words
  10   = exceptional vocabulary, precise and expressive throughout

Text to evaluate:
\"\"\"{text}\"\"\""""


def tone_prompt(text: str) -> str:
    """
    Prompt for tone_evaluator_node.
    Evaluates: consistency of voice, formality level, audience alignment,
    whether the tone matches the writing's apparent purpose.

    Args:
        text (str): the raw writing submitted by the user

    Returns:
        str: formatted prompt string ready for llm.with_structured_output().invoke()
    """
    return f"""You are an expert writing evaluator specializing in tone assessment.

Evaluate the tone of the following text.
Consider: consistency of voice throughout, appropriateness of formality level,
alignment with the intended audience, whether tone shifts unexpectedly,
whether the tone matches the apparent purpose of the writing.

Score scale:
  0–3  = inconsistent or completely inappropriate tone
  4–5  = tone is partially appropriate but shifts or misses the audience
  6–7  = mostly appropriate tone with minor inconsistencies
  8–9  = consistent and well-matched tone throughout
  10   = perfect tone — exactly right for the format, purpose, and audience

Text to evaluate:
\"\"\"{text}\"\"\""""


def readability_prompt(text: str) -> str:
    """
    Prompt for readability_evaluator_node.
    Evaluates: sentence length variation, passive voice ratio, lexical density,
    reading ease — how effortless it is to read through the writing.

    Args:
        text (str): the raw writing submitted by the user

    Returns:
        str: formatted prompt string ready for llm.with_structured_output().invoke()
    """
    return f"""You are an expert writing evaluator specializing in readability assessment.

Evaluate how readable the following text is.
Consider: variation in sentence length, overuse of passive voice, lexical
density (ratio of content words to total words), paragraph length,
overall reading ease and flow.

Score scale:
  0–3  = very hard to read, dense and exhausting
  4–5  = readable but effortful, some heavy passages
  6–7  = generally readable with occasional dense sections
  8–9  = easy and enjoyable to read throughout
  10   = effortlessly readable, perfect pacing and flow

Text to evaluate:
\"\"\"{text}\"\"\""""


def argument_prompt(text: str) -> str:
    """
    Prompt for argument_structure_node.
    Evaluates argument quality across 5 dimensions.
    Output is captured by ArgumentOutput Pydantic schema in schemas.py.

    Args:
        text (str): the raw writing submitted by the user

    Returns:
        str: formatted prompt string ready for llm.with_structured_output().invoke()
    """
    return f"""You are an expert writing evaluator specializing in argument analysis.

Analyze the argumentative structure of the following text across these 5 dimensions:

1. claim_presence        — does the text make a clear central claim or thesis?
2. supporting_evidence   — quality of evidence: "none", "weak", "moderate", or "strong"
3. reasoning_quality     — quality of logical reasoning: "poor", "fair", "good", or "excellent"
4. counterargument_usage — does the text acknowledge or address opposing views?
5. critical_thinking_depth — depth of analytical thinking: "surface", "moderate", or "deep"

Text to evaluate:
\"\"\"{text}\"\"\""""


def feedback_prompt(scores: dict, format_type: str, text: str) -> str:
    """
    Prompt for feedback_generator_node.
    Takes all computed scores + format type and generates structured improvement feedback.
    This is the final LLM call — output is captured by FeedbackOutput in schemas.py.

    Args:
        scores (dict):     all dimension scores from the parallel evaluator nodes.
                           keys: grammar, clarity, coherence, depth, structure,
                                 vocabulary, tone, readability
        format_type (str): detected format — "paragraph", "essay", or "article"
        text (str):        the original writing (so Claude gives text-specific feedback)

    Returns:
        str: formatted prompt string ready for llm.with_structured_output().invoke()
    """
    # Build a readable score summary to inject into the prompt
    score_lines = "\n".join(
        f"  {dim.capitalize()}: {score}/10"
        for dim, score in scores.items()
    )

    return f"""You are an expert writing coach providing detailed, actionable feedback.

The following {format_type} has been evaluated across 8 dimensions:

{score_lines}

Original text:
\"\"\"{text}\"\"\"

Based on the scores and the text above, generate structured improvement feedback.
Be specific — reference actual phrases or patterns from the text where possible.
Provide 3 strengths, 3 weaknesses, 3 revision steps, 2 style adjustments,
and a predicted score band with a one-sentence justification."""
