from app.state import ReviewState
from config.settings import URGENCY_TO_PRIORITY


def priority_node(state: ReviewState) -> dict:
    urgency = state["diagnosis"].urgency
    return {"priority": URGENCY_TO_PRIORITY[urgency]}
