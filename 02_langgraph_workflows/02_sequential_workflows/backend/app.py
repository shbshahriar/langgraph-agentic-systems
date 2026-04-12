# ── app.py ────────────────────────────────────────────────────────────────────
# FastAPI application entry point.
#
# Responsibilities:
#   1. Serve the frontend HTML file at GET /
#   2. Expose the note generation API at POST /generate_note
#
# How the frontend is served:
#   FileResponse returns the index.html file directly from the server.
#   This means you only need to run one server — no separate frontend server.
#   Path(__file__).resolve() gives the absolute path of this file, then we
#   navigate up two levels (.parent.parent) to reach the project root and
#   into the 'frontend' folder.
#
# Run the server with:
#   uv run uvicorn app:app --app-dir 02_langgraph_workflows/02_sequential_workflows/backend
# ──────────────────────────────────────────────────────────────────────────────

from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from schemas import NoteRequest, NoteResponse
from workflow import workflow

app = FastAPI()

# Resolve the absolute path to the frontend directory at startup.
# Structure: backend/app.py → parent = backend/ → parent.parent = 02_sequential_workflows/
# Then: 02_sequential_workflows/frontend/index.html
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@app.get("/")
def serve_frontend():
    """Serve the frontend HTML page.

    Called when the user opens http://127.0.0.1:8000 in the browser.
    Returns the index.html file with the correct text/html content type.
    """
    return FileResponse(FRONTEND_DIR / "index.html", media_type="text/html")


@app.post("/generate_note", response_model=NoteResponse)
async def generate_note(request: NoteRequest):
    """Run the LangGraph workflow and return outline, notes, and summary.

    Flow:
      1. Receive the topic from the request body (validated by NoteRequest)
      2. Pass it into the compiled LangGraph workflow as initial state
      3. The workflow runs: outline → notes → summary nodes sequentially
      4. Extract the results from the final state and return as NoteResponse
    """
    # Invoke the graph with only the required input key.
    # The workflow fills in 'outline', 'notes', 'summary' as it runs.
    result = workflow.invoke({'topic': request.text})

    return NoteResponse(
        outline=result['outline'],
        notes=result['notes'],
        summary=result['summary'],
    )
