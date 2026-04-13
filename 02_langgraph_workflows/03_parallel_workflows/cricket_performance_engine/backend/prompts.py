# prompts.py
# Prompt builder functions for the three LLM nodes in CAPE.
# Each function takes only what it needs and returns a plain string.


def batting_insight_prompt(metrics: dict) -> str:
    """Prompt for batting_insight_node.
    Receives the computed batting metrics dict and asks for an evaluation.
    """
    return (
        f"You are a cricket analyst. Based on the following batting metrics, "
        f"write a short structured evaluation in 3-4 sentences. "
        f"Use plain text only — no markdown, no asterisks, no bold, no bullet points.\n\n"
        f"Batting Metrics:\n"
        f"  Strike Rate       : {metrics.get('strike_rate', 'N/A')}\n"
        f"  Boundary Ratio    : {metrics.get('boundary_ratio', 'N/A')}\n"
        f"  Dot Ball %        : {metrics.get('dot_ball_percentage', 'N/A')}\n\n"
        f"Evaluate the player's batting style, aggression, and consistency."
    )


def bowling_insight_prompt(metrics: dict) -> str:
    """Prompt for bowling_insight_node.
    Receives the computed bowling metrics dict and asks for an evaluation.
    """
    return (
        f"You are a cricket analyst. Based on the following bowling metrics, "
        f"write a short structured evaluation in 3-4 sentences. "
        f"Use plain text only — no markdown, no asterisks, no bold, no bullet points.\n\n"
        f"Bowling Metrics:\n"
        f"  Economy Rate       : {metrics.get('economy_rate', 'N/A')}\n"
        f"  Bowling Average    : {metrics.get('bowling_average', 'N/A')}\n"
        f"  Bowling Strike Rate: {metrics.get('bowling_strike_rate', 'N/A')}\n\n"
        f"Evaluate the player's effectiveness, control, and wicket-taking ability."
    )


def insight_generator_prompt(
    batting_metrics: dict,
    bowling_metrics: dict,
    impact_score: float,
    player_role: str
) -> str:
    """Prompt for insight_generator_node.
    Combines everything into a final scouting report.
    """
    return (
        f"You are a professional cricket scout. Generate a concise scouting report "
        f"based on the data below. Include: strengths, weaknesses, recommended team role, "
        f"and format suitability (T20 / ODI / Test). "
        f"Use plain text only — no markdown, no asterisks, no bold, no bullet points.\n\n"
        f"Player Role    : {player_role}\n"
        f"Impact Score   : {impact_score:.1f} / 100\n\n"
        f"Batting Metrics: {batting_metrics}\n"
        f"Bowling Metrics: {bowling_metrics}\n\n"
        f"Keep the report under 150 words."
    )
