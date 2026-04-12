from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Optional

class NoteRequest(BaseModel):

    text: Annotated[str, Field(..., description="The title of the note",max_length=200,min_length=3)]

class NoteResponse(BaseModel):

    outline: str
    notes: str
    summary: str

    