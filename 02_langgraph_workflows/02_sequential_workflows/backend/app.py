from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from schemas import NoteRequest, NoteResponse
from workflow import workflow

app = FastAPI()

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

@app.get("/")
def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html", media_type="text/html")

@app.post("/generate_note", response_model=NoteResponse)
async def generate_note(request: NoteRequest):
    result = workflow.invoke({'topic': request.text})
    return NoteResponse(
        outline=result['outline'],
        notes=result['notes'],
        summary=result['summary'],
    )
