from pydantic import BaseModel, Field
from typing import Annotated, Literal


class SentimentOutput(BaseModel):
    sentiment: Annotated[
        Literal["positive", "negative", "neutral"],
        Field(description="Overall sentiment expressed in the user review"),
    ]
    confidence: Annotated[
        float,
        Field(ge=0.0, le=1.0, description="Model confidence in the sentiment label (0-1)"),
    ]
    reasoning: Annotated[
        str,
        Field(description="Short explanation of why this sentiment label was chosen"),
    ]
