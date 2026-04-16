from app.state import ReviewState


def sentiment_router(state: ReviewState) -> str:
    sentiment = state["sentiment"].sentiment
    if sentiment == "positive":
        return "appreciation_response"
    if sentiment == "neutral":
        return "neutral_response"
    return "diagnosis_node"


def priority_router(state: ReviewState) -> str:
    if state.get("escalation_flag"):
        return "escalation_response"
    return "support_response"
