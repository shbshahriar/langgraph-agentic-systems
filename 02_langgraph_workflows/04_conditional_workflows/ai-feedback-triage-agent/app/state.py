from typing import Literal, TypedDict

from app.schemas.sentiment_schema import SentimentOutput
from app.schemas.diagnosis_schema import DiagnosisOutput


class ReviewState(TypedDict):
    review: str

    sentiment: SentimentOutput
    diagnosis: DiagnosisOutput

    priority: Literal["P0", "P1", "P2", "P3"]
    escalation_flag: bool

    response: str
