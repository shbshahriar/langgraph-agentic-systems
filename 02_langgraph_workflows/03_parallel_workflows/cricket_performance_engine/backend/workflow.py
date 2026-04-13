# workflow.py
# Builds and compiles the CAPE LangGraph StateGraph.
#
# Graph structure (parallel fan-out / fan-in):
#
#   START
#     └─► input_parser
#               ├─► batting_pipeline ─► batting_insight_node ─┐
#               └─► bowling_pipeline ─► bowling_insight_node ─┤
#                                                             ↓
#                                              performance_fusion_node
#                                                             ↓
#                                              insight_generator_node
#                                                             ↓
#                                                            END
#
# Key LangGraph concepts used here:
#   add_node  — registers a node function under a name
#   add_edge  — sequential edge (A always goes to B)
#   compiled  — .compile() locks the graph and returns a runnable

from langgraph.graph import StateGraph, START, END

from state import CricketState
from nodes import (
    input_parser,
    batting_pipeline,
    bowling_pipeline,
    batting_insight_node,
    bowling_insight_node,
    performance_fusion_node,
    insight_generator_node,
)

# ── Build the graph ────────────────────────────────────────────────────────────

builder = StateGraph(CricketState)

# Register all 7 nodes
builder.add_node("input_parser",           input_parser)
builder.add_node("batting_pipeline",       batting_pipeline)
builder.add_node("bowling_pipeline",       bowling_pipeline)
builder.add_node("batting_insight_node",   batting_insight_node)
builder.add_node("bowling_insight_node",   bowling_insight_node)
builder.add_node("performance_fusion_node", performance_fusion_node)
builder.add_node("insight_generator_node", insight_generator_node)

# ── Wire the edges ─────────────────────────────────────────────────────────────

# Entry point
builder.add_edge(START, "input_parser")

# Fan-out: input_parser triggers both branches in parallel
builder.add_edge("input_parser", "batting_pipeline")
builder.add_edge("input_parser", "bowling_pipeline")

# Each branch continues to its LLM insight node
builder.add_edge("batting_pipeline",     "batting_insight_node")
builder.add_edge("bowling_pipeline",     "bowling_insight_node")

# Fan-in: both insight nodes must complete before fusion runs
# LangGraph waits automatically when multiple edges point to the same node
builder.add_edge("batting_insight_node", "performance_fusion_node")
builder.add_edge("bowling_insight_node", "performance_fusion_node")

# Sequential tail
builder.add_edge("performance_fusion_node", "insight_generator_node")
builder.add_edge("insight_generator_node",  END)

# ── Compile ────────────────────────────────────────────────────────────────────

# cricket_graph is the runnable object imported by app.py
cricket_graph = builder.compile()
