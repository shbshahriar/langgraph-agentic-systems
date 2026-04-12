# ── prompts.py ────────────────────────────────────────────────────────────────
# Contains all prompt-building functions for each node in the workflow.
#
# Why plain f-strings instead of LangChain PromptTemplate?
#   PromptTemplate adds value when you need LCEL chains (prompt | llm | parser)
#   or reusable partial variables. Here, each node calls its prompt function
#   directly with state values — f-strings are simpler and equally effective.
#
# Each function takes only what it needs from the state and returns a plain
# string that gets passed directly to llm.invoke().
# ──────────────────────────────────────────────────────────────────────────────

def outline_prompt(topic: str) -> str:
    """Build a prompt that asks the LLM to produce a 5-point outline."""
    return f"Create an outline for a note on the topic in just 5 points: {topic}"


def notes_prompt(topic: str, outline: str) -> str:
    """Build a prompt that asks the LLM to expand the outline into detailed notes.

    Receives the outline produced by the previous node so the notes stay
    aligned with the structure already generated.
    """
    return (
        f"Based on the following outline, write detailed notes on the topic "
        f"but not more than 500 char: {topic}\n\nOutline:\n{outline}"
    )


def summary_prompt(topic: str, notes: str) -> str:
    """Build a prompt that asks the LLM to condense the notes into a short summary."""
    return (
        f"Summarize the following notes on the topic but not more than 50 characters: "
        f"{topic}\n\nNotes:\n{notes}"
    )
