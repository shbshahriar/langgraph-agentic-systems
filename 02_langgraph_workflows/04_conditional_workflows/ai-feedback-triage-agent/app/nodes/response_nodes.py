from app.state import ReviewState
from services.llm_service import get_llm


APPRECIATION_PROMPT = """You are a warm customer-success writer. The user left a positive
review. Write a short (2-3 sentence) thank-you reply that feels personal and specific
to what they said.

Review:
\"\"\"{review}\"\"\"
"""

NEUTRAL_PROMPT = """You are a polite support writer. The user left a neutral review.
Write a short (2-3 sentence) acknowledgement that invites more specific feedback.

Review:
\"\"\"{review}\"\"\"
"""

SUPPORT_PROMPT = """You are a support agent. The user left a negative review. Write a
short (3-4 sentence) empathetic reply that:
- acknowledges the specific issue
- outlines the next step their {department} team will take
- sets expectations for follow-up (priority {priority})

Issue summary: {summary}
Tone detected: {tone}

Review:
\"\"\"{review}\"\"\"
"""

ESCALATION_PROMPT = """You are a senior support lead handling a CRITICAL (P0) ticket.
Write a short (3-4 sentence) reply that:
- acknowledges the severity directly
- confirms the issue has been escalated to the {department} team
- promises a direct follow-up within 24 hours
- avoids generic apologies

Issue summary: {summary}
Tone detected: {tone}

Review:
\"\"\"{review}\"\"\"
"""


def _generate(prompt: str) -> str:
    result = get_llm().invoke(prompt)
    content = result.content
    if isinstance(content, list):
        return "".join(str(part) for part in content)
    return content


def appreciation_response(state: ReviewState) -> dict:
    return {"response": _generate(APPRECIATION_PROMPT.format(review=state["review"]))}


def neutral_response(state: ReviewState) -> dict:
    return {"response": _generate(NEUTRAL_PROMPT.format(review=state["review"]))}


def support_response(state: ReviewState) -> dict:
    diagnosis = state["diagnosis"]
    prompt = SUPPORT_PROMPT.format(
        review=state["review"],
        department=diagnosis.department,
        priority=state["priority"],
        summary=diagnosis.summary,
        tone=diagnosis.tone,
    )
    return {"response": _generate(prompt)}


def escalation_response(state: ReviewState) -> dict:
    diagnosis = state["diagnosis"]
    prompt = ESCALATION_PROMPT.format(
        review=state["review"],
        department=diagnosis.department,
        summary=diagnosis.summary,
        tone=diagnosis.tone,
    )
    return {"response": _generate(prompt)}
