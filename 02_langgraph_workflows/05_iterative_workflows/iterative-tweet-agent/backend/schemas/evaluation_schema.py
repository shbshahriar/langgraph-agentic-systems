from pydantic import BaseModel, Field
from typing import Literal, Annotated


class TweetEvaluation(BaseModel):
    evaluation:Annotated[Literal["approved", "needs_improvement"], Field(..., description="Final evaluation result.")]
    feedback: Annotated[str, Field(..., description="Feedback for the tweet.")]
