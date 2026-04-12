# ── workflow.py ───────────────────────────────────────────────────────────────
# Builds and compiles the LangGraph sequential workflow.
#
# What is a StateGraph?
#   A StateGraph is LangGraph's core building block. You register nodes
#   (functions) and edges (connections between nodes), then compile it into
#   a runnable object that can be invoked like a function.
#
# Sequential workflow — how it works:
#   START → outline → notes → summary → END
#
#   Each arrow is an edge. LangGraph executes nodes one after another in the
#   order the edges define. The state dict is passed through and updated at
#   every step.
#
# START / END:
#   Special LangGraph constants. START marks where the graph enters; END marks
#   where it exits. They are not nodes — only used in add_edge() calls.
#
# graph.compile():
#   Validates the graph (no disconnected nodes, no missing edges) and returns
#   a CompiledGraph object. This is what you call .invoke() on.
# ──────────────────────────────────────────────────────────────────────────────

from langgraph.graph import StateGraph, START, END
from state import NoteState
from nodes import generate_outline, generate_notes, generate_summary

# Initialise the graph with NoteState as the shared state schema
graph = StateGraph(NoteState)

# ── Register nodes ────────────────────────────────────────────────────────────
graph.add_node("outline", generate_outline)   # Node 1
graph.add_node("notes",   generate_notes)     # Node 2
graph.add_node("summary", generate_summary)   # Node 3

# ── Define execution order (edges) ───────────────────────────────────────────
graph.add_edge(START,     "outline")   # Entry point → outline
graph.add_edge("outline", "notes")    # outline → notes
graph.add_edge("notes",   "summary")  # notes → summary
graph.add_edge("summary", END)        # summary → exit

# Compile into a runnable graph — imported and used by app.py
workflow = graph.compile()
