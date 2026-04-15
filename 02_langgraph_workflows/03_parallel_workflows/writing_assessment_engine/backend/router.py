# =============================================================================
# router.py — Format classification logic for the Writing Assessment Engine
#
# This file contains ONE function: classify_format(text) → str
#
# It detects whether the submitted text is:
#   "paragraph" — short standalone writing (default / fallback)
#   "essay"     — structured academic writing with thesis and argument
#   "article"   — journalistic or informational writing citing sources
#
# WHY NOT USE AN LLM FOR CLASSIFICATION?
#   The router runs BEFORE any LLM call — it's a lightweight gate that decides
#   the format so the rest of the pipeline can tailor its feedback.
#   Using an LLM here would add cost and latency to every single request
#   just to produce a single label that simple keyword heuristics can handle.
#   Deterministic rules are faster, free, and consistent.
#
# DETECTION STRATEGY — 3 steps:
#   1. Word count gate  — very short text is always "paragraph"
#   2. Keyword scoring  — count how many format-specific keywords appear
#   3. Decision logic   — highest keyword score wins, with word count as guard
#
# IMPORTS:
#   config.py → FORMAT_KEYWORDS, FORMAT_MIN_WORDS
# =============================================================================

from config import FORMAT_KEYWORDS, FORMAT_MIN_WORDS


def classify_format(text: str) -> str:
    """
    Classify the submitted writing into one of three formats:
    "paragraph", "essay", or "article".

    Detection runs in 3 steps:

    STEP 1 — Word count gate:
        Count the total words in the text.
        If word count < FORMAT_MIN_WORDS["paragraph"] (30), return "paragraph"
        immediately — the text is too short to be anything else.

    STEP 2 — Keyword scoring:
        Convert the text to lowercase and count how many keywords from
        FORMAT_KEYWORDS["essay"] and FORMAT_KEYWORDS["article"] appear.
        Each keyword match adds 1 to that format's score.

    STEP 3 — Decision with word count guard:
        - If essay_score > article_score AND word count >= FORMAT_MIN_WORDS["essay"]:
              return "essay"
        - If article_score > essay_score AND word count >= FORMAT_MIN_WORDS["article"]:
              return "article"
        - If essay_score > article_score but word count < FORMAT_MIN_WORDS["essay"]:
              text has essay language but is too short → return "paragraph"
        - If both scores are equal (tie) or both are 0:
              return "paragraph" (safe fallback)

    Args:
        text (str): the raw writing submitted by the user

    Returns:
        str: one of "paragraph", "essay", or "article"

    Examples:
        classify_format("The cat sat on the mat.")
        → "paragraph"  (too short, < 30 words)

        classify_format("In conclusion, this essay argues that climate change
                         requires immediate policy intervention. Furthermore,
                         the evidence presented supports the thesis that...")
        → "essay"  (essay keywords: "in conclusion", "furthermore", "thesis")

        classify_format("According to researchers at MIT, a new study shows
                         that renewable energy adoption has accelerated.
                         Experts interviewed by the journal reported...")
        → "article"  (article keywords: "according to", "study shows",
                       "researchers", "experts", "interviewed")
    """

    # -------------------------------------------------------------------------
    # STEP 1 — Word count gate
    # Split text on whitespace to count words.
    # If the text is shorter than the minimum paragraph length, it's a paragraph.
    # -------------------------------------------------------------------------

    words = text.split()
    word_count = len(words)

    if word_count < FORMAT_MIN_WORDS["paragraph"]:
        # Too short to classify as anything meaningful
        return "paragraph"

    # -------------------------------------------------------------------------
    # STEP 2 — Keyword scoring
    # Lowercase the text once so keyword matching is case-insensitive.
    # Then count how many essay keywords and article keywords appear.
    # We use 'in text_lower' rather than exact word matching because many
    # keywords are multi-word phrases (e.g. "in conclusion", "study shows").
    # -------------------------------------------------------------------------

    text_lower = text.lower()

    essay_score = sum(
        1 for keyword in FORMAT_KEYWORDS["essay"]
        if keyword in text_lower
    )

    article_score = sum(
        1 for keyword in FORMAT_KEYWORDS["article"]
        if keyword in text_lower
    )

    # -------------------------------------------------------------------------
    # STEP 3 — Decision with word count guard
    # Keyword score tells us the FORMAT INTENT of the text.
    # Word count guard ensures the text is long enough to actually BE that format.
    #
    # Example: a 60-word text with "in conclusion" scores essay keywords,
    # but 60 words is not long enough to be a real essay → classify as paragraph.
    # -------------------------------------------------------------------------

    if essay_score > article_score:
        # Text leans toward essay — check if it meets the minimum word count
        if word_count >= FORMAT_MIN_WORDS["essay"]:
            return "essay"
        else:
            # Has essay language but is too short to be a full essay
            return "paragraph"

    elif article_score > essay_score:
        # Text leans toward article — check if it meets the minimum word count
        if word_count >= FORMAT_MIN_WORDS["article"]:
            return "article"
        else:
            # Has article language but is too short to be a full article
            return "paragraph"

    else:
        # Tie (both scores equal, including both = 0).
        # No clear keyword signal — use word count as the fallback heuristic.
        # Long texts with no clear markers are more likely essays than paragraphs.
        if word_count >= FORMAT_MIN_WORDS["essay"]:
            return "essay"
        return "paragraph"
