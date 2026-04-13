# nodes.py
# All 7 node functions for the CAPE parallel workflow.
#
# Execution order (defined in workflow.py):
#
#   START → input_parser
#             ├── batting_pipeline  ──► batting_insight_node ──┐
#             └── bowling_pipeline  ──► bowling_insight_node ──┤
#                                                              ↓
#                                               performance_fusion_node
#                                                              ↓
#                                               insight_generator_node
#                                                              ↓
#                                                             END
#
# Node rules (same as sequential workflow):
#   - Receives the full state as input
#   - Returns ONLY the keys it wants to update
#   - LangGraph merges those updates back into state automatically

from state import CricketState
from prompts import batting_insight_prompt, bowling_insight_prompt, insight_generator_prompt
from llm import get_llm
from config import (
    STRIKE_RATE_POWER_HITTER, STRIKE_RATE_ANCHOR,
    ECONOMY_CONTROLLER, WICKETS_ALL_ROUNDER,
    BATTING_WEIGHT, BOWLING_WEIGHT
)

# Single shared LLM client — created once, reused by all LLM nodes
llm = get_llm()


def _text(response) -> str:
    """Extract plain text from an LLM response.

    Newer versions of langchain-google-genai return response.content as a list
    of content blocks: [{'type': 'text', 'text': '...'}]
    Older versions return a plain string.
    This helper handles both so the nodes don't need to care.
    """
    content = response.content
    if isinstance(content, str):
        return content
    # List of content blocks — join all text parts
    return "".join(
        block["text"]
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    )


# ── Node 1 ─────────────────────────────────────────────────────────────────────

def input_parser(state: CricketState) -> dict:  # noqa: ARG001
    """Validate and pass through the raw inputs.

    Reads:  all 7 input fields
    Writes: nothing (returns empty dict — inputs are already in state)

    This node is the single entry point after START. It ensures inputs
    exist before the graph fans out into parallel branches.
    """
    return {}


# ── Node 2 (parallel branch 1) ─────────────────────────────────────────────────

def batting_pipeline(state: CricketState) -> dict:
    """Calculate all batting metrics from raw inputs.

    Reads:  runs, balls, fours, sixes
    Writes: batting_metrics

    Returns empty dict when balls=0 (player did not bat).
    Metrics computed:
      strike_rate        = runs / balls × 100
      boundary_ratio     = boundary runs / total runs
      dot_ball_percentage= estimated dot balls / total balls × 100
    """
    balls = state['balls']

    # Player did not bat — skip all calculations
    if balls == 0:
        return {'batting_metrics': {}}

    runs  = state['runs']
    fours = state['fours']
    sixes = state['sixes']

    strike_rate = round((runs / balls) * 100, 2)

    boundary_runs  = (fours * 4) + (sixes * 6)
    boundary_ratio = round(boundary_runs / runs, 2) if runs > 0 else 0.0

    non_boundary_runs   = runs - boundary_runs
    scoring_balls       = fours + sixes + non_boundary_runs
    dot_balls           = max(0, balls - scoring_balls)
    dot_ball_percentage = round((dot_balls / balls) * 100, 2)

    return {
        'batting_metrics': {
            'strike_rate'        : strike_rate,
            'boundary_ratio'     : boundary_ratio,
            'dot_ball_percentage': dot_ball_percentage,
        }
    }


# ── Node 3 (parallel branch 2) ─────────────────────────────────────────────────

def bowling_pipeline(state: CricketState) -> dict:
    """Calculate all bowling metrics from raw inputs.

    Reads:  overs, runs_conceded, wickets
    Writes: bowling_metrics

    Returns empty dict when overs=0 (player did not bowl).
    Metrics computed:
      economy_rate        = runs_conceded / overs
      bowling_average     = runs_conceded / wickets  (N/A if no wickets)
      bowling_strike_rate = balls_bowled / wickets   (N/A if no wickets)
    """
    overs = state['overs']

    # Player did not bowl — skip all calculations
    if overs == 0:
        return {'bowling_metrics': {}}

    runs_conceded = state['runs_conceded']
    wickets       = state['wickets']
    balls_bowled  = round(overs * 6)

    economy_rate = round(runs_conceded / overs, 2)

    bowling_average     = round(runs_conceded / wickets, 2) if wickets > 0 else None
    bowling_strike_rate = round(balls_bowled / wickets, 2)  if wickets > 0 else None

    return {
        'bowling_metrics': {
            'economy_rate'       : economy_rate,
            'bowling_average'    : bowling_average,
            'bowling_strike_rate': bowling_strike_rate,
        }
    }


# ── Node 4 (after batting_pipeline) ───────────────────────────────────────────

def batting_insight_node(state: CricketState) -> dict:
    """Generate a short LLM evaluation of the batting metrics.

    Reads:  batting_metrics
    Writes: batting_metrics (adds 'batting_insight' key via reducer merge)
    Skips LLM call if player did not bat (empty metrics).
    """
    if not state['batting_metrics']:
        return {'batting_metrics': {}}
    response = llm.invoke(batting_insight_prompt(state['batting_metrics']))
    return {
        'batting_metrics': {'batting_insight': _text(response)}
    }


# ── Node 5 (after bowling_pipeline) ───────────────────────────────────────────

def bowling_insight_node(state: CricketState) -> dict:
    """Generate a short LLM evaluation of the bowling metrics.

    Reads:  bowling_metrics
    Writes: bowling_metrics (adds 'bowling_insight' key via reducer merge)
    Skips LLM call if player did not bowl (empty metrics).
    """
    if not state['bowling_metrics']:
        return {'bowling_metrics': {}}
    response = llm.invoke(bowling_insight_prompt(state['bowling_metrics']))
    return {
        'bowling_metrics': {'bowling_insight': _text(response)}
    }


# ── Node 6 ─────────────────────────────────────────────────────────────────────

def performance_fusion_node(state: CricketState) -> dict:
    """Combine batting and bowling metrics into an impact score and player role.

    Reads:  batting_metrics, bowling_metrics
    Writes: impact_score, player_role

    Impact score (0-100):
      Batting contribution = normalised strike rate × BATTING_WEIGHT
      Bowling contribution = normalised economy  × BOWLING_WEIGHT

    Player role is determined by strike rate and economy rate thresholds
    defined in config.py.
    """
    batting = state['batting_metrics']
    bowling = state['bowling_metrics']

    has_batting = bool(batting)
    has_bowling = bool(bowling)

    strike_rate  = batting.get('strike_rate', 0)
    economy_rate = bowling.get('economy_rate', 10)

    # ── Impact score ──────────────────────────────────────────────────────────
    # Use full weight on the active discipline when the other is absent.
    if has_batting and has_bowling:
        batting_score = min(strike_rate / 200 * 100, 100)
        bowling_score = max(0, (15 - economy_rate) / 15 * 100)
        impact_score  = round(
            (batting_score * BATTING_WEIGHT) + (bowling_score * BOWLING_WEIGHT), 1
        )
    elif has_batting:
        batting_score = min(strike_rate / 200 * 100, 100)
        impact_score  = round(batting_score, 1)
    else:
        bowling_score = max(0, (15 - economy_rate) / 15 * 100)
        impact_score  = round(bowling_score, 1)

    # ── Player role classifier ────────────────────────────────────────────────
    wickets = state['wickets']

    if has_batting and not has_bowling:
        # Pure batsman — classify purely on strike rate
        role = "power_hitter" if strike_rate >= STRIKE_RATE_POWER_HITTER else "top_order_anchor"
    elif has_bowling and not has_batting:
        # Pure bowler — classify purely on economy and wickets
        role = "economy_controller" if economy_rate <= ECONOMY_CONTROLLER else "death_over_specialist"
    elif strike_rate >= STRIKE_RATE_POWER_HITTER:
        role = "power_hitter"
    elif strike_rate <= STRIKE_RATE_ANCHOR:
        role = "top_order_anchor"
    elif economy_rate <= ECONOMY_CONTROLLER and wickets >= WICKETS_ALL_ROUNDER:
        role = "economy_controller"
    elif wickets >= WICKETS_ALL_ROUNDER and strike_rate >= STRIKE_RATE_ANCHOR:
        role = "balanced_all_rounder"
    else:
        role = "death_over_specialist"

    return {
        'impact_score': impact_score,
        'player_role' : role,
    }


# ── Node 7 ─────────────────────────────────────────────────────────────────────

def insight_generator_node(state: CricketState) -> dict:
    """Generate the final AI scouting report.

    Reads:  batting_metrics, bowling_metrics, impact_score, player_role
    Writes: final_report
    """
    response = llm.invoke(
        insight_generator_prompt(
            batting_metrics = state['batting_metrics'],
            bowling_metrics = state['bowling_metrics'],
            impact_score    = state.get('impact_score', 0.0),
            player_role     = state.get('player_role', 'unknown'),
        )
    )
    return {'final_report': _text(response)}
