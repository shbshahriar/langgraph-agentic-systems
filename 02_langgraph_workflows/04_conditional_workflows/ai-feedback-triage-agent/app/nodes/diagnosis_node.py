from app.state import ReviewState
from app.schemas.diagnosis_schema import DiagnosisOutput
from services.llm_service import get_llm


DIAGNOSIS_PROMPT = """You are a support triage specialist. Analyze the following negative
user review and extract structured metadata.

For each field pick one of the allowed values:
- issue_type: bug, performance, ux, billing, feature_request, support, other
- tone: angry, frustrated, confused, neutral, polite
- urgency: low, medium, high, critical
- department: engineering, product, support, billing

Also provide a one-line summary of the core issue.

Review:
\"\"\"{review}\"\"\"
"""


def diagnosis_node(state: ReviewState) -> dict:
    llm = get_llm().with_structured_output(DiagnosisOutput)
    result: DiagnosisOutput = llm.invoke(
        DIAGNOSIS_PROMPT.format(review=state["review"])
    )
    return {"diagnosis": result}
