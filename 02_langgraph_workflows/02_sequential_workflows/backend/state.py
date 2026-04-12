from typing import TypedDict, NotRequired

class NoteState(TypedDict):
    topic: str
    outline: NotRequired[str]
    notes: NotRequired[str]
    summary: NotRequired[str]