# ── nodes.py ──────────────────────────────────────────────────────────────────
# Defines the three processing nodes of the LangGraph workflow.
#
# How LangGraph nodes work:
#   - Each node is a plain Python function.
#   - It receives the full current state as a dict.
#   - It must return a dict containing ONLY the keys it wants to update.
#   - LangGraph merges the returned dict into the state before calling the next node.
#
# Node execution order (defined in workflow.py):
#   generate_outline → generate_notes → generate_summary
#
# Why llm is instantiated once at module level?
#   Calling get_llm() creates a new API client. Doing that inside each function
#   would create a new client on every invocation, which is wasteful.
#   Creating it once here means all three nodes share a single client instance.
# ──────────────────────────────────────────────────────────────────────────────

from prompts import outline_prompt, notes_prompt, summary_prompt
from state import NoteState
from llm import get_llm

# Single shared LLM client used by all nodes
llm = get_llm()


def generate_outline(state: NoteState) -> dict:
    """Node 1 — Generate a structured outline from the topic.

    Reads:  state['topic']
    Writes: state['outline']
    """
    response = llm.invoke(outline_prompt(state['topic']))
    return {'outline': response.content}


def generate_notes(state: NoteState) -> dict:
    """Node 2 — Expand the outline into detailed notes.

    Reads:  state['topic'], state['outline']
    Writes: state['notes']

    Uses .get() instead of [] for 'outline' because it is NotRequired in
    NoteState. In practice, the graph sequence guarantees 'outline' is always
    set by the time this node runs, but .get() satisfies the type checker.
    """
    response = llm.invoke(notes_prompt(state['topic'], state.get('outline', '')))
    return {'notes': response.content}


def generate_summary(state: NoteState) -> dict:
    """Node 3 — Summarise the notes into a concise paragraph.

    Reads:  state['topic'], state['notes']
    Writes: state['summary']
    """
    response = llm.invoke(summary_prompt(state['topic'], state.get('notes', '')))
    return {'summary': response.content}
