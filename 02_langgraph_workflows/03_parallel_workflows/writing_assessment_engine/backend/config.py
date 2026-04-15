# =============================================================================
# config.py — Central configuration for the Parallel Writing Assessment Engine
#
# This file has NO imports and NO logic.
# Every other file in the backend imports constants from here.
# Changing a value here affects the entire system — one place, full control.
# =============================================================================


# -----------------------------------------------------------------------------
# LLM SETTINGS
# These control which AI model is used and how it behaves.
#
# MODEL_NAME  : The Claude model we send prompts to via langchain-anthropic.
#               "claude-haiku-4-5-20251001" is the fastest Claude model — ideal for parallel scoring.
#
# TEMPERATURE : Controls randomness in LLM output.
#               0.0 = fully deterministic (same input → same output every time)
#               1.0 = very creative / unpredictable
#               0.3 = slightly flexible but mostly consistent — ideal for scoring
# -----------------------------------------------------------------------------

MODEL_NAME  = "claude-haiku-4-5-20251001"  # fastest Claude model — ideal for parallel scoring
TEMPERATURE = 0.3


# -----------------------------------------------------------------------------
# SCORING SCALE
# All 8 evaluator nodes return a score within this range.
# MIN_SCORE = 0  (worst possible)
# MAX_SCORE = 10 (best possible)
# -----------------------------------------------------------------------------

MIN_SCORE = 0
MAX_SCORE = 10


# -----------------------------------------------------------------------------
# SCORE WEIGHTS
# The final score is a weighted average of all 8 dimension scores.
# Each weight represents how much that dimension contributes to the total.
#
# Rule: all values must sum to exactly 1.0
#
# Why these weights?
#   - grammar, clarity, readability are the most universally important → 0.15 each
#   - depth, structure, vocabulary, tone matter but are more format-specific → 0.10 each
#   - coherence bridges all sections together → 0.15
#
# Formula used in evaluation_merger_node:
#   final_score = sum(score[dim] * SCORE_WEIGHTS[dim] for dim in SCORE_WEIGHTS)
# -----------------------------------------------------------------------------

SCORE_WEIGHTS = {
    "grammar":     0.15,  # correctness of sentences, punctuation, spelling
    "clarity":     0.15,  # how easy the writing is to understand
    "coherence":   0.15,  # how well ideas connect and flow between sections
    "depth":       0.10,  # how thoroughly topics are explored
    "structure":   0.10,  # logical organization of the content
    "vocabulary":  0.10,  # word choice, variety, appropriateness
    "tone":        0.10,  # formality, consistency, audience fit
    "readability": 0.15,  # sentence length, complexity, reading ease
}


# -----------------------------------------------------------------------------
# FORMAT DETECTION KEYWORDS
# Used by router.py to classify the submitted text into one of three formats:
#   - "essay"     : academic writing with a thesis and structured argument
#   - "article"   : journalistic or informational writing citing sources/facts
#   - "paragraph" : short standalone writing — the fallback if neither matches
#
# How detection works (in router.py):
#   1. Count how many essay keywords appear in the text
#   2. Count how many article keywords appear in the text
#   3. Whichever count is higher → that format wins
#   4. If both counts are 0 or tied → default to "paragraph"
# -----------------------------------------------------------------------------

FORMAT_KEYWORDS = {
    "essay": [
        # Closing / opening structure markers
        "thesis",
        "introduction",
        "in conclusion",
        "to conclude",
        "in summary",
        "to summarize",
        "conclusion",

        # Argumentative connectors (very common in real essays)
        "furthermore",
        "moreover",
        "however",
        "nevertheless",
        "therefore",
        "thus",
        "consequently",
        "as a result",
        "in addition",
        "on the other hand",
        "in contrast",
        "despite",
        "although",

        # Argument / opinion signals
        "argument",
        "argue",
        "claim",
        "evidence",
        "critics",
        "proponents",
        "advocates",
        "in my opinion",
        "one can argue",
        "this demonstrates",
        "this suggests",

        # Academic elaboration phrases
        "for example",
        "for instance",
        "to illustrate",
        "research shows",
        "studies show",
        "evidence suggests",
        "it is clear",

        # Ordered enumeration (first... second... finally)
        "firstly",
        "secondly",
        "thirdly",
        "finally",
    ],
    "article": [
        # Citation / attribution (core journalistic signals)
        "according to",
        "reported",
        "published",
        "sources say",
        "officials say",
        "announced",
        "revealed",
        "confirmed",
        "said in a statement",

        # Article-specific structure
        "headline",
        "journalists",
        "news",
        "interviewed",

        # Research / data references (common in feature articles)
        "study shows",
        "study found",
        "research found",
        "researchers",
        "experts",
        "study",
        "survey",
        "analysis",
        "findings",
        "statistics",
        "data shows",
        "data",
        "report",

        # Scale / numbers (ubiquitous in journalism)
        "percent",
        "per cent",
        "million",
        "billion",

        # Institutional and industry language
        "government",
        "industry",
        "market",
        "infrastructure",
        "investment",
        "policy",
        "sector",
        "organisation",
        "organization",
    ],
    "paragraph": [],      # no keywords — detected by elimination (fallback)
}


# -----------------------------------------------------------------------------
# FORMAT MINIMUM WORD COUNTS
# Used alongside keyword detection to avoid misclassifying very short inputs.
#
# If a text has essay keywords but only 50 words, it's likely a paragraph.
# router.py uses these thresholds as a secondary check after keyword matching.
#
# paragraph : anything >= 30 words qualifies as a paragraph
# essay     : needs at least 200 words to be a meaningful essay
# article   : needs at least 150 words to contain enough journalistic content
# -----------------------------------------------------------------------------

FORMAT_MIN_WORDS = {
    "paragraph": 30,
    "essay":     150,   # lowered from 200 — real essays can be under 200 words
    "article":   120,   # lowered from 150 — short feature articles exist
}

# -----------------------------------------------------------------------------
# FORMAT MAXIMUM WORD COUNTS
# Upper word count limits used by router.py as a secondary classification check.
#
# If a text exceeds the max for its detected format, router.py may reclassify it.
# Example: a 600-word text with article keywords but > 500 words → likely an essay.
#
# paragraph : anything above 100 words is too long to be a simple paragraph
# essay     : essays can go up to 1000 words before becoming a long-form article
# article   : articles typically stay under 500 words in this system's scope
# -----------------------------------------------------------------------------

FORMAT_MAX_WORDS = {
    "paragraph": 100,
    "essay":     1000,
    "article":   500,
}