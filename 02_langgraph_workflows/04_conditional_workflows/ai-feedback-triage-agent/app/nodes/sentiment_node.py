from app.state import ReviewState
from app.schemas.sentiment_schema import SentimentOutput
from services.llm_service import get_llm


SENTIMENT_PROMPT = """You are a customer-feedback analyst. Classify the sentiment of the
following user review as positive, negative, or neutral. Return a confidence score
between 0 and 1 and a one-sentence reasoning.

Review:
\"\"\"{review}\"\"\"
"""


def sentiment_node(state: ReviewState) -> dict:
    llm = get_llm().with_structured_output(SentimentOutput)
    result: SentimentOutput = llm.invoke(
        SENTIMENT_PROMPT.format(review=state["review"])
    )
    return {"sentiment": result}
