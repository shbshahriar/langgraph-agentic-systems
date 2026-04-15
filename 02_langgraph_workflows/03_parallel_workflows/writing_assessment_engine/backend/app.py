# =============================================================================
# app.py - FastAPI server for the Parallel Writing Assessment Engine
#
# Serves BOTH the frontend (static files) and the backend API from one
# uvicorn process. Open http://localhost:8000 to use the app.
#
# CRITICAL IMPORT ORDER:
#   load_dotenv() MUST run BEFORE "from workflow import graph"
#   because workflow.py -> nodes.py -> llm.py -> ChatAnthropic() reads the key.
#
# TO RUN:
#   cd writing_assessment_engine/backend
#   uvicorn app:app --reload --port 8000
#
#   http://localhost:8000        <- frontend UI
#   http://localhost:8000/docs   <- Swagger UI
# =============================================================================

# Standard library
import os
from pathlib import Path
from typing import cast

# Third-party - environment loading (must happen before LangGraph imports)
from dotenv import load_dotenv

load_dotenv()  # must be first - loads ANTHROPIC_API_KEY into os.environ

# Third-party - FastAPI framework
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles   # serves a directory of files
from fastapi.responses import FileResponse    # sends a single file as a response

# Internal - schemas for request/response validation
from schemas import WritingRequest, WritingResponse

# Internal - compiled LangGraph graph (imported AFTER load_dotenv)
from workflow import graph

# Internal - state type (used only for cast() to satisfy Pyright)
from state import WritingState


# =============================================================================
# PATHS
#
# Resolve the frontend directory relative to this file:
#   __file__        -> .../backend/app.py
#   .parent         -> .../backend/
#   .parent.parent  -> .../writing_assessment_engine/
#   / "frontend"    -> .../writing_assessment_engine/frontend/
# =============================================================================

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


# =============================================================================
# APP INSTANCE
# =============================================================================

app = FastAPI(
    title="Parallel Writing Assessment Engine",
    description=(
        "Evaluates writing across 8 dimensions in parallel using Claude. "
        "Supports paragraph, essay, and article formats."
    ),
    version="1.0.0",
)


# =============================================================================
# CORS MIDDLEWARE
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# ROOT ROUTE - serves index.html
#
# StaticFiles can serve /static/style.css etc. but it does NOT handle the root
# path "/". This explicit GET / route fills that gap by returning index.html
# via FileResponse (correct Content-Type: text/html, streamed from disk).
# =============================================================================

@app.get("/")
def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


# =============================================================================
# STATIC FILES - serves style.css and main.js at /static/<filename>
#
# index.html references:
#   <link rel="stylesheet" href="/static/style.css" />
#   <script src="/static/main.js"></script>
#
# This mount MUST come after all @app.get / @app.post routes - FastAPI matches
# routes top-to-bottom, and StaticFiles would swallow "/" if mounted first.
# =============================================================================

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.get("/health")
def health_check():
    return {"status": "ok"}


# =============================================================================
# MAIN ENDPOINT: POST /evaluate-writing
# =============================================================================

@app.post("/evaluate-writing", response_model=WritingResponse)
def evaluate_writing(request: WritingRequest) -> WritingResponse:
    """
    Run the full LangGraph writing assessment pipeline.

    Pipeline stages:
        1. format_classifier_node         - detects format (no LLM)
        2. [parallel] 8 evaluator nodes   - score all dimensions
        3. [parallel] argument_structure   - evaluate argument quality
        4. evaluation_merger_node          - compute final_score, build breakdown
        5. feedback_generator_node         - generate improvement report
    """

    try:
        # graph.invoke() expects WritingState per Pyright, but LangGraph also
        # accepts a plain dict at runtime. cast() is a zero-cost type hint that
        # silences the Pyright error without changing runtime behaviour.
        final_state = graph.invoke(cast(WritingState, {"text": request.text}))

        return WritingResponse(
            format_type       = final_state["format_type"],
            dimension_scores  = final_state["dimension_breakdown"],
            argument_analysis = final_state["argument_analysis"],
            final_score       = final_state["final_score"],
            feedback_report   = final_state["feedback_report"],
            error             = None,
        )

    except Exception as e:
        # Return a structured error so the frontend can display a message.
        # HTTP 200 is intentional - the frontend reads data.error, not status.
        return WritingResponse(
            format_type       = "unknown",
            dimension_scores  = {},
            argument_analysis = {},
            final_score       = 0.0,
            feedback_report   = {},
            error             = str(e),
        )
