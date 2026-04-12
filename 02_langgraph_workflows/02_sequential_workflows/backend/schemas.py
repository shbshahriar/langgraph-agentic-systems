# ── schemas.py ────────────────────────────────────────────────────────────────
# Pydantic models that define the shape of HTTP request and response bodies.
#
# Why Pydantic and not plain dicts?
#   FastAPI uses Pydantic models to automatically:
#     - Parse and validate incoming JSON request bodies
#     - Serialize outgoing response data to JSON
#     - Generate OpenAPI (Swagger) documentation at /docs
#
# NoteRequest  — what the client sends to POST /generate_note
# NoteResponse — what the server sends back
# ──────────────────────────────────────────────────────────────────────────────

from pydantic import BaseModel, Field
from typing import Annotated


class NoteRequest(BaseModel):
    # The topic the user wants to generate notes for.
    # Annotated with Field to enforce length constraints:
    #   - min_length=3  : prevents empty or near-empty topics
    #   - max_length=200: prevents excessively long inputs
    text: Annotated[
        str,
        Field(..., description="The topic to generate notes for", min_length=3, max_length=200)
    ]


class NoteResponse(BaseModel):
    # The three outputs produced by the LangGraph workflow nodes.
    # These map directly to the keys written into NoteState during the run.
    outline: str    # 5-point structured outline (from generate_outline node)
    notes: str      # Detailed notes based on the outline (from generate_notes node)
    summary: str    # Short summary of the notes (from generate_summary node)
