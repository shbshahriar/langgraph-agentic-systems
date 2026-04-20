from pydantic import BaseModel, Field
from typing import Annotated


class TweetRequest(BaseModel):
    topic: Annotated[str, Field(..., description="Topic to generate a tweet about.")]
    max_iteration: Annotated[int, Field(default=5, description="Maximum number of refinement iterations.")]
