# app.py
# FastAPI entry point for the CAPE backend.
#
# Responsibilities:
#   1. Load environment variables (GOOGLE_API_KEY) before any LLM import
#   2. Serve the frontend (index.html, style.css, main.js) as static files
#   3. Expose POST /analyze-player — runs the LangGraph workflow and returns results
#
# Run with:
#   uvicorn app:app --reload --port 8000
#
# The frontend is served from ../frontend/ relative to this file.
# When the browser hits http://localhost:8000 it gets index.html,
# which then calls POST /analyze-player via fetch().

from pathlib import Path

from dotenv import load_dotenv

# load_dotenv MUST come before importing workflow/nodes/llm
# because those modules create the LLM client at import time,
# and the client needs GOOGLE_API_KEY to already be in os.environ.
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from schemas import PlayerRequest, PlayerResponse
from state import CricketState
from workflow import cricket_graph

# ── App setup ──────────────────────────────────────────────────────────────────

app = FastAPI(
    title="CAPE — Cricket Performance Intelligence Engine",
    description="Parallel LangGraph pipeline that analyses batting and bowling stats.",
    version="1.0.0",
)

# ── Static files ───────────────────────────────────────────────────────────────

# Resolve the frontend folder relative to this file so it works
# regardless of where uvicorn is launched from.
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
def serve_index():
    """Serve the frontend index.html at the root URL."""
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(str(index_path))


# Mount frontend assets at /assets — keeps API routes unambiguous.
# index.html must reference /assets/style.css and /assets/main.js.
app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.post("/analyze-player", response_model=PlayerResponse)
def analyze_player(request: PlayerRequest):
    """Run the CAPE parallel workflow and return the full analysis.

    Steps:
      1. Convert the Pydantic request into a plain dict (LangGraph state)
      2. Invoke the compiled graph — runs all 7 nodes
      3. Extract the output fields and return as PlayerResponse
    """
    # Build initial state — typed as CricketState so invoke() accepts it
    initial_state: CricketState = {  # type: ignore[misc]
        "runs"         : request.runs,
        "balls"        : request.balls,
        "fours"        : request.fours,
        "sixes"        : request.sixes,
        "overs"        : request.overs,
        "runs_conceded": request.runs_conceded,
        "wickets"      : request.wickets,
    }

    try:
        result = cricket_graph.invoke(initial_state)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return PlayerResponse(
        batting_metrics=result["batting_metrics"],
        bowling_metrics=result["bowling_metrics"],
        impact_score   =result["impact_score"],
        player_role    =result["player_role"],
        final_report   =result["final_report"],
    )
