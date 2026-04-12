# ── app.py ────────────────────────────────────────────────────────────────────
# FastAPI application entry point.
#
# Responsibilities:
#   1. Load environment variables from .env (must happen before any LLM import)
#   2. Serve the frontend HTML file at GET /
#   3. Expose the note generation API at POST /generate_note
#
# Why load_dotenv() is called here (not in llm.py):
#   Environment variables must be available before LangChain initialises its
#   clients. Calling it once at startup — before importing workflow — ensures
#   GOOGLE_API_KEY is set in time. Spreading load_dotenv() across modules
#   risks it running too late or multiple times unnecessarily.
#
# How the frontend is served:
#   FileResponse returns the index.html file directly from the server.
#   This means you only need to run one server — no separate frontend server.
#   Path(__file__).resolve() gives the absolute path of this file, then we
#   navigate up one level (.parent) to reach backend/, then up again (.parent)
#   to reach 02_sequential_workflows/, and into the 'frontend' folder.
#
# Run the server with:
#   uv run uvicorn app:app --app-dir 02_langgraph_workflows/02_sequential_workflows/backend
# ──────────────────────────────────────────────────────────────────────────────

from pathlib import Path
from dotenv import load_dotenv

# Load .env before importing workflow, which triggers LLM client initialisation.
# GOOGLE_API_KEY must be in the environment before ChatGoogleGenerativeAI is created.
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from schemas import NoteRequest, NoteResponse
from workflow import workflow

app = FastAPI(
    title="Note Generator",
    version="1.0.0",
    description="Generates a structured outline, detailed notes, and a summary for any topic using a LangGraph sequential workflow.",
)

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

    Raises:
      HTTPException 500: if the workflow fails (e.g. API key error, LLM timeout)
    """
    try:
        # Invoke the graph with only the required input key.
        # The workflow fills in 'outline', 'notes', 'summary' as it runs.
        result = workflow.invoke({'topic': request.text})
    except Exception as e:
        # Catch any LLM or graph execution errors and return a clean 500
        # response instead of leaking an internal traceback to the client.
        raise HTTPException(status_code=500, detail=f"Workflow failed: {e}")

    return NoteResponse(
        outline=result['outline'],
        notes=result['notes'],
        summary=result['summary'],
    )
