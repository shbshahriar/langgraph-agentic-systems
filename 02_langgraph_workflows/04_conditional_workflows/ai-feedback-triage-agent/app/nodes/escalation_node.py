from app.state import ReviewState
from config.settings import CRITICAL_PRIORITY


def escalation_node(state: ReviewState) -> dict:
    is_critical = state.get("priority") == CRITICAL_PRIORITY
    return {"escalation_flag": is_critical}
