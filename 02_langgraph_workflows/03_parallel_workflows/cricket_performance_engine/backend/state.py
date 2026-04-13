# state.py
# Defines the single shared state that flows through every node in the graph.
#
# In LangGraph, state is like a shared notebook passed from node to node.
# Each node reads what it needs and writes only what it produces.
# LangGraph merges those writes back automatically before the next node runs.
#
# ── Why Annotated on batting_metrics and bowling_metrics? ─────────────────────
# In a sequential workflow, only one node writes at a time so plain types work.
# In a parallel workflow, batting nodes and bowling nodes run AT THE SAME TIME.
# If two nodes try to write to the same key simultaneously, LangGraph needs to
# know HOW to combine those writes — that is what the reducer function does.
# Annotated[dict, reducer_fn] tells LangGraph: "use this function to merge".
# ─────────────────────────────────────────────────────────────────────────────

from typing import TypedDict, NotRequired, Annotated
from reducers import merge_batting_metrics, merge_bowling_metrics


class CricketState(TypedDict):

    # ── Raw inputs (provided by the user at invoke time) ──────────────────────
    runs          : int     # Total runs scored
    balls         : int     # Total balls faced
    fours         : int     # Number of fours hit
    sixes         : int     # Number of sixes hit
    overs         : float   # Overs bowled
    runs_conceded : int     # Runs given away while bowling
    wickets       : int     # Wickets taken

    # ── Parallel outputs (written by batting and bowling nodes in parallel) ────
    # Annotated tells LangGraph to use the reducer when merging concurrent writes
    batting_metrics : Annotated[dict, merge_batting_metrics]
    bowling_metrics : Annotated[dict, merge_bowling_metrics]

    # ── Fusion outputs (written by performance_fusion_node) ───────────────────
    impact_score : NotRequired[float]   # Combined batting + bowling score (0-100)
    player_role  : NotRequired[str]     # e.g. "power_hitter", "economy_controller"

    # ── Final output (written by insight_generator_node) ─────────────────────
    final_report : NotRequired[str]     # AI generated scouting summary
