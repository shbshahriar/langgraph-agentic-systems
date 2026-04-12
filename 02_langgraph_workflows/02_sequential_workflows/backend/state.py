# ── state.py ──────────────────────────────────────────────────────────────────
# Defines the shared state object that flows through every node in the graph.
#
# LangGraph passes this state dict from node to node. Each node receives the
# current state, does its work, and returns ONLY the keys it wants to update.
# LangGraph then merges those updates back into the state automatically.
#
# Why TypedDict?
#   Provides type hints for the state dict so editors and type checkers can
#   catch mistakes (e.g. accessing a key that doesn't exist).
#
# Why NotRequired?
#   'topic' is the only input — the user provides it at invocation time.
#   'outline', 'notes', 'summary' are populated progressively by the nodes,
#   so they don't exist yet when the graph starts. Marking them NotRequired
#   lets us invoke the graph with just {'topic': '...'} without type errors.
# ──────────────────────────────────────────────────────────────────────────────

from typing import TypedDict, NotRequired

class NoteState(TypedDict):
    topic: str              # Input: the subject the user wants notes on
    outline: NotRequired[str]   # Set by generate_outline node
    notes: NotRequired[str]     # Set by generate_notes node
    summary: NotRequired[str]   # Set by generate_summary node
