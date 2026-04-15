# =============================================================================
# workflow.py — LangGraph graph definition for the Writing Assessment Engine
#
# This file has ONE job: wire all 11 nodes into a StateGraph and compile it.
#
# WHAT THIS FILE DOES NOT DO:
#   - No LLM calls
#   - No prompt building
#   - No state logic
#   - No FastAPI routing
#
# All of that lives in nodes.py, prompts.py, and app.py respectively.
# This file is purely the graph structure — who runs, in what order.
#
# =============================================================================
#
# GRAPH EXECUTION FLOW:
#
#   START
#     │
#     ▼
#   format_classifier_node          ← detects "paragraph", "essay", "article"
#     │
#     ├── grammar_evaluator_node ───────────────────────────────────────────┐
#     ├── clarity_evaluator_node ──────────────────────────────────────────┤
#     ├── coherence_evaluator_node ───────────────────────────────────────┤
#     ├── depth_evaluator_node ───────────────────────────────────────────┤
#     ├── structure_evaluator_node ─────────────────────────────────────── ┤  (parallel)
#     ├── vocabulary_evaluator_node ───────────────────────────────────────┤
#     ├── tone_evaluator_node ──────────────────────────────────────────── ┤
#     ├── readability_evaluator_node ──────────────────────────────────────┤
#     └── argument_structure_node ─────────────────────────────────────────┘
#                                                                           │
#                                                                           ▼
#                                                              evaluation_merger_node
#                                                                           │
#                                                                           ▼
#                                                              feedback_generator_node
#                                                                           │
#                                                                           ▼
#                                                                          END
#
# KEY CONCEPT — Fan-out / Fan-in:
#   Fan-out: one node (format_classifier) connects to MANY nodes at once
#            → LangGraph runs them all in parallel (separate threads)
#   Fan-in:  MANY nodes all connect to ONE node (evaluation_merger)
#            → LangGraph waits for ALL of them to finish before proceeding
#
# =============================================================================
#
# IMPORTS:
#   langgraph.graph → StateGraph, START, END
#   state.py        → WritingState (the shared state TypedDict)
#   nodes.py        → all 11 node functions
# =============================================================================

from langgraph.graph import StateGraph, START, END

from state import WritingState
from nodes import (
    format_classifier_node,
    grammar_evaluator_node,
    clarity_evaluator_node,
    coherence_evaluator_node,
    depth_evaluator_node,
    structure_evaluator_node,
    vocabulary_evaluator_node,
    tone_evaluator_node,
    readability_evaluator_node,
    argument_structure_node,
    evaluation_merger_node,
    feedback_generator_node,
)


def build_graph():
    """
    Construct and compile the LangGraph StateGraph for the Writing Assessment Engine.

    This function is called ONCE at app startup (in app.py) and the compiled
    graph is stored as a module-level variable. Every API request then calls
    graph.invoke({"text": ...}) to run the full pipeline.

    WHY A FUNCTION instead of module-level graph?
        Same reason as get_llm() in llm.py — module-level code runs immediately
        on import. Wrapping in a function lets app.py control WHEN the graph
        is built (after load_dotenv() has run and all imports are ready).

    Returns:
        CompiledGraph: the compiled LangGraph graph, ready to call .invoke() on
    """

    # -------------------------------------------------------------------------
    # STEP 1 — Create the StateGraph.
    #
    # StateGraph(WritingState) tells LangGraph:
    #   "the shared state flowing between all nodes is a WritingState TypedDict"
    #
    # Every node receives the full state as input and returns a partial dict
    # that LangGraph merges back using the reducers defined in state.py.
    # -------------------------------------------------------------------------

    graph = StateGraph(WritingState)

    # -------------------------------------------------------------------------
    # STEP 2 — Register all nodes.
    #
    # .add_node("string_name", function) does two things:
    #   1. Registers the function under a label used in .add_edge() calls
    #   2. Tells LangGraph the node exists in this graph
    #
    # The string name is only used for graph wiring — it doesn't affect
    # how the function runs or what it returns.
    # -------------------------------------------------------------------------

    # Stage 1: Format detection (no LLM)
    graph.add_node("format_classifier",       format_classifier_node)

    # Stage 2: Parallel LLM evaluators (all 8 run simultaneously)
    graph.add_node("grammar_evaluator",       grammar_evaluator_node)
    graph.add_node("clarity_evaluator",       clarity_evaluator_node)
    graph.add_node("coherence_evaluator",     coherence_evaluator_node)
    graph.add_node("depth_evaluator",         depth_evaluator_node)
    graph.add_node("structure_evaluator",     structure_evaluator_node)
    graph.add_node("vocabulary_evaluator",    vocabulary_evaluator_node)
    graph.add_node("tone_evaluator",          tone_evaluator_node)
    graph.add_node("readability_evaluator",   readability_evaluator_node)

    # Stage 3: Argument analysis (runs in parallel with stage 2)
    graph.add_node("argument_structure",      argument_structure_node)

    # Stage 4: Merge all scores (runs after all parallel nodes finish)
    graph.add_node("evaluation_merger",       evaluation_merger_node)

    # Stage 5: Generate feedback (runs last, after merger)
    graph.add_node("feedback_generator",      feedback_generator_node)

    # -------------------------------------------------------------------------
    # STEP 3 — Wire the entry point.
    #
    # START is a special LangGraph sentinel that represents the graph's input.
    # This edge says: "when the graph is invoked, run format_classifier first."
    # -------------------------------------------------------------------------

    graph.add_edge(START, "format_classifier")

    # -------------------------------------------------------------------------
    # STEP 4 — Fan-out: connect format_classifier to all 9 parallel nodes.
    #
    # Each .add_edge("format_classifier", "X") creates a separate branch.
    # LangGraph sees that format_classifier has MULTIPLE outgoing edges and
    # launches all 9 target nodes simultaneously in separate threads.
    #
    # WHY NOT USE add_conditional_edges() here?
    #   add_conditional_edges() is for routing to DIFFERENT nodes based on a
    #   condition (e.g. route to essay_pipeline OR article_pipeline based on
    #   format_type). Here we always run ALL 9 nodes regardless of format —
    #   so simple add_edge() for each branch is the correct approach.
    # -------------------------------------------------------------------------

    graph.add_edge("format_classifier", "grammar_evaluator")
    graph.add_edge("format_classifier", "clarity_evaluator")
    graph.add_edge("format_classifier", "coherence_evaluator")
    graph.add_edge("format_classifier", "depth_evaluator")
    graph.add_edge("format_classifier", "structure_evaluator")
    graph.add_edge("format_classifier", "vocabulary_evaluator")
    graph.add_edge("format_classifier", "tone_evaluator")
    graph.add_edge("format_classifier", "readability_evaluator")
    graph.add_edge("format_classifier", "argument_structure")

    # -------------------------------------------------------------------------
    # STEP 5 — Fan-in: wait for ALL 9 parallel nodes, then run merger.
    #
    # add_edge(list_of_sources, target) is the fan-in pattern in LangGraph.
    # LangGraph will NOT run "evaluation_merger" until every node in the list
    # has written its result back to WritingState.
    #
    # This is what makes safe parallel execution possible:
    #   - All 9 nodes run concurrently
    #   - Each writes its output field (grammar_score, clarity_score, etc.)
    #   - The reducers in state.py merge concurrent writes safely
    #   - Once all 9 are done, evaluation_merger_node runs with full state
    # -------------------------------------------------------------------------

    graph.add_edge(
        [
            "grammar_evaluator",
            "clarity_evaluator",
            "coherence_evaluator",
            "depth_evaluator",
            "structure_evaluator",
            "vocabulary_evaluator",
            "tone_evaluator",
            "readability_evaluator",
            "argument_structure",
        ],
        "evaluation_merger"
    )

    # -------------------------------------------------------------------------
    # STEP 6 — Sequential edges after the parallel section.
    #
    # After evaluation_merger finishes (final_score + dimension_breakdown ready),
    # run feedback_generator to produce the improvement report.
    # After feedback_generator finishes, the graph ends.
    # -------------------------------------------------------------------------

    graph.add_edge("evaluation_merger",  "feedback_generator")
    graph.add_edge("feedback_generator", END)

    # -------------------------------------------------------------------------
    # STEP 7 — Compile the graph.
    #
    # .compile() validates the graph structure (no missing nodes, no dead ends)
    # and returns a CompiledGraph object that exposes:
    #   .invoke(input_dict)         — synchronous execution
    #   .ainvoke(input_dict)        — async execution
    #   .stream(input_dict)         — streaming execution (yields state updates)
    #   .get_graph().draw_mermaid() — generate a Mermaid diagram of the graph
    #
    # We use .invoke() in app.py for simplicity.
    # -------------------------------------------------------------------------

    return graph.compile()


# =============================================================================
# MODULE-LEVEL COMPILED GRAPH
#
# build_graph() is called once here so that workflow.py exports a ready-to-use
# compiled graph. app.py imports this directly:
#
#   from workflow import graph
#   result = graph.invoke({"text": user_text})
#
# Because build_graph() is a function (not module-level code), it only runs
# when workflow.py is imported — by which time app.py has already called
# load_dotenv() and all environment variables are available.
# =============================================================================

graph = build_graph()
