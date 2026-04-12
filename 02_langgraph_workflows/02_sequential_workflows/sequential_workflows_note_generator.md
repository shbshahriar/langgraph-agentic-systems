# Sequential Workflows — Note Generator

> **A full-stack LangGraph application: how a sequential prompt-chaining workflow goes from graph definition to a running web API with a browser frontend**

This project builds a **Note Generator** — enter a topic, get back a structured outline, detailed notes, and a concise summary. It is the practical implementation of the **Prompt Chaining** workflow pattern: each LLM call's output becomes the next call's input, flowing through a LangGraph `StateGraph` from start to finish.

---

## Table of Contents

1. [What Is a Sequential Workflow?](#1-what-is-a-sequential-workflow)
2. [Project Structure](#2-project-structure)
3. [How the Pieces Fit Together](#3-how-the-pieces-fit-together)
4. [The State — Shared Memory](#4-the-state--shared-memory)
5. [The Prompts](#5-the-prompts)
6. [The LLM Factory](#6-the-llm-factory)
7. [The Nodes — Processing Steps](#7-the-nodes--processing-steps)
8. [The Workflow — Graph Definition](#8-the-workflow--graph-definition)
9. [The API — FastAPI Backend](#9-the-api--fastapi-backend)
10. [The Frontend](#10-the-frontend)
11. [Running the Application](#11-running-the-application)
12. [Key Design Decisions](#12-key-design-decisions)

---

## 1. What Is a Sequential Workflow?

A sequential workflow runs nodes **one after another in a fixed order**. Each node reads from the shared state, does its work, and writes its result back. The next node picks up where the previous one left off.

```
START → outline → notes → summary → END
```

This is the **Prompt Chaining** pattern: the output of one LLM call is the direct input to the next, building up a richer result at each step.

**When to use it:**
- Tasks that are inherently ordered (you can't summarise notes that don't exist yet)
- Each step needs the output of the previous step as context
- You want to keep each LLM call focused on a single, bounded concern

---

## 2. Project Structure

```
02_sequential_workflows/
├── backend/
│   ├── __init__.py       # Marks backend as a Python package
│   ├── state.py          # NoteState TypedDict — shared graph state
│   ├── prompts.py        # f-string prompt builders for each node
│   ├── llm.py            # LLM factory — returns a ChatGoogleGenerativeAI instance
│   ├── nodes.py          # Three node functions: outline, notes, summary
│   ├── workflow.py       # StateGraph definition and compilation
│   ├── schemas.py        # Pydantic request/response models for the API
│   └── app.py            # FastAPI entry point — serves frontend + API
├── frontend/
│   └── index.html        # Self-contained single-file browser UI
└── notebook/
    ├── 01_bmi_calculation.ipynb    # Sequential workflow basics with BMI example
    ├── 02_simple_llm.ipynb         # Simple single-node LLM workflow
    └── 03_prompt_chaining.ipynb    # Prompt chaining notebook exploration
```

---

## 3. How the Pieces Fit Together

```
Browser (index.html)
    │
    │  POST /generate_note  { "text": "Quantum Computing" }
    ▼
FastAPI (app.py)
    │
    │  workflow.invoke({ "topic": "Quantum Computing" })
    ▼
LangGraph StateGraph
    │
    ├── Node 1: generate_outline  →  writes state["outline"]
    ├── Node 2: generate_notes    →  reads outline, writes state["notes"]
    └── Node 3: generate_summary  →  reads notes,   writes state["summary"]
    │
    │  returns { outline, notes, summary }
    ▼
FastAPI (NoteResponse)
    │
    │  JSON response to browser
    ▼
Browser renders markdown in three panels
```

Every module has a single responsibility. Changing the LLM model only requires editing `llm.py`. Changing what the prompts say only requires editing `prompts.py`. The graph wiring lives entirely in `workflow.py`.

---

## 4. The State — Shared Memory

**File:** `backend/state.py`

```python
from typing import TypedDict, NotRequired

class NoteState(TypedDict):
    topic: str                    # Required — provided by the caller
    outline: NotRequired[str]     # Written by Node 1
    notes:   NotRequired[str]     # Written by Node 2
    summary: NotRequired[str]     # Written by Node 3
```

The state is a `TypedDict` — a typed Python dict. It is the single object passed from node to node throughout the entire workflow run.

**Why `NotRequired` for outline, notes, summary?**

When the graph is first invoked, only `topic` exists. The other three fields are created progressively as each node runs. Marking them `NotRequired` lets you call `workflow.invoke({'topic': '...'})` without type errors — you don't have to provide values that haven't been generated yet.

**The rule every node follows:**
1. Read fields it needs from `state`
2. Do its work (call the LLM)
3. Return **only** the dict keys it wants to update — LangGraph merges them in

---

## 5. The Prompts

**File:** `backend/prompts.py`

```python
def outline_prompt(topic: str) -> str:
    return f"Create an outline for a note on the topic in just 5 points: {topic}"

def notes_prompt(topic: str, outline: str) -> str:
    return (
        f"Based on the following outline, write detailed notes on the topic "
        f"but not more than 500 char: {topic}\n\nOutline:\n{outline}"
    )

def summary_prompt(topic: str, notes: str) -> str:
    return (
        f"Summarize the following notes on the topic but not more than 50 characters: "
        f"{topic}\n\nNotes:\n{notes}"
    )
```

Each function takes exactly the state values it needs and returns a plain string. The string goes directly into `llm.invoke()`.

**Why f-strings instead of `PromptTemplate`?**

`PromptTemplate` adds value when you need LCEL chains (`prompt | llm | parser`) or reusable partial variables across many places. Here, each node calls its builder directly — f-strings are simpler and equally effective. No extra abstraction needed.

---

## 6. The LLM Factory

**File:** `backend/llm.py`

```python
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7
    )
```

`get_llm()` is a factory function that creates and returns a configured LLM client. It is called **once** at module level in `nodes.py`:

```python
llm = get_llm()  # Single shared instance used by all three nodes
```

**Why a factory function?** If you need to swap the model or provider, you change it in one place. Separating configuration from usage makes `nodes.py` independent of the specific LLM being used.

**Why is `load_dotenv()` not here?** Environment variables must be loaded before any LangChain client initialises. Loading them in `app.py` at startup — before any imports that depend on env vars — ensures `GOOGLE_API_KEY` is available in time. Scattering `load_dotenv()` across modules risks it running too late.

---

## 7. The Nodes — Processing Steps

**File:** `backend/nodes.py`

```python
from prompts import outline_prompt, notes_prompt, summary_prompt
from state import NoteState
from llm import get_llm

llm = get_llm()  # Single shared client

def generate_outline(state: NoteState) -> dict:
    response = llm.invoke(outline_prompt(state['topic']))
    return {'outline': response.content}

def generate_notes(state: NoteState) -> dict:
    response = llm.invoke(notes_prompt(state['topic'], state.get('outline', '')))
    return {'notes': response.content}

def generate_summary(state: NoteState) -> dict:
    response = llm.invoke(summary_prompt(state['topic'], state.get('notes', '')))
    return {'summary': response.content}
```

**Key points:**

| Detail | Reason |
|--------|--------|
| Return `dict`, not string | LangGraph requires a dict to know which state keys to update |
| `state.get('outline', '')` not `state['outline']` | `outline` is `NotRequired` — `.get()` satisfies the type checker safely |
| `llm` instantiated once at module level | Avoids creating a new API client on every node call |

Each node is a plain Python function — no base class, no decorator required. LangGraph treats any callable with this signature as a valid node.

---

## 8. The Workflow — Graph Definition

**File:** `backend/workflow.py`

```python
from langgraph.graph import StateGraph, START, END
from state import NoteState
from nodes import generate_outline, generate_notes, generate_summary

graph = StateGraph(NoteState)

graph.add_node("outline", generate_outline)
graph.add_node("notes",   generate_notes)
graph.add_node("summary", generate_summary)

graph.add_edge(START,     "outline")
graph.add_edge("outline", "notes")
graph.add_edge("notes",   "summary")
graph.add_edge("summary", END)

workflow = graph.compile()
```

**`StateGraph(NoteState)`** — creates a graph whose shared state follows the `NoteState` schema.

**`add_node(name, fn)`** — registers a function as a named node.

**`add_edge(from, to)`** — defines execution order. `START` and `END` are LangGraph constants marking entry and exit; they are not nodes themselves.

**`graph.compile()`** — validates the graph (checks for disconnected nodes, missing edges, undefined entry points) and returns a `CompiledGraph` that can be invoked. This is what `app.py` imports as `workflow`.

**Execution flow:**
```
START
  └── outline  (generate_outline runs, state["outline"] set)
        └── notes    (generate_notes runs, state["notes"] set)
              └── summary  (generate_summary runs, state["summary"] set)
                    └── END
```

---

## 9. The API — FastAPI Backend

**File:** `backend/app.py`

```python
from dotenv import load_dotenv
load_dotenv()  # Must run before importing workflow (which imports the LLM)

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from schemas import NoteRequest, NoteResponse
from workflow import workflow

app = FastAPI(
    title="Note Generator",
    version="1.0.0",
    description="...",
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

@app.get("/")
def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html", media_type="text/html")

@app.post("/generate_note", response_model=NoteResponse)
async def generate_note(request: NoteRequest):
    try:
        result = workflow.invoke({'topic': request.text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow failed: {e}")
    return NoteResponse(
        outline=result['outline'],
        notes=result['notes'],
        summary=result['summary'],
    )
```

**Design decisions:**

| Decision | Reason |
|----------|--------|
| `load_dotenv()` before imports | `GOOGLE_API_KEY` must exist before `ChatGoogleGenerativeAI` initialises |
| `Path(__file__).resolve()` | Gives an absolute path that works regardless of the working directory when the server starts |
| `FileResponse` (not `StaticFiles`) | Simpler for a single HTML file — no mount conflicts, no extra routes |
| `HTTPException(500)` on workflow failure | Returns a clean JSON error to the client instead of leaking an internal traceback |
| `response_model=NoteResponse` | FastAPI auto-validates and serialises the response, and generates `/docs` schema |

**Pydantic schemas** (`backend/schemas.py`):

```python
class NoteRequest(BaseModel):
    text: Annotated[str, Field(..., min_length=3, max_length=200)]

class NoteResponse(BaseModel):
    outline: str
    notes: str
    summary: str
```

`NoteRequest` validates the incoming JSON. `NoteResponse` defines the exact shape returned to the client.

---

## 10. The Frontend

**File:** `frontend/index.html`

A single self-contained HTML file served directly by FastAPI. It requires no build step, no npm, no framework.

**Key parts:**

```
┌─────────────────────────────────┐
│         Note Generator          │  ← Header with gradient title
├─────────────────────────────────┤
│  [Enter topic...] [Generate]    │  ← Input row
│         ○ (spinner)             │  ← Shown during API call
├─────────────────────────────────┤
│  ● Outline                      │
│  ● Notes                        │  ← Three result sections
│  ● Summary                      │
└─────────────────────────────────┘
```

**How it calls the API:**

```javascript
const API_URL = '/generate_note';  // Relative URL — no hardcoded port

const res = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: topic }),
});
const data = await res.json();
```

Using a relative URL (`/generate_note` instead of `http://127.0.0.1:8000/generate_note`) means the frontend works on any port without modification, because it always calls back to the same server that served the page.

**Markdown rendering:**

The LLM returns markdown-formatted text (`**bold**`, `## headings`, `* bullets`). A `renderMarkdown()` helper converts this to HTML before injecting it into the DOM with `innerHTML`. This is done client-side with regex so no external library is needed.

---

## 11. Running the Application

**1. Set up environment variables** — copy `.env.example` to `.env` and add your `GOOGLE_API_KEY`:

```
GOOGLE_API_KEY=your_key_here
```

**2. Install dependencies:**

```bash
uv sync
```

**3. Start the server:**

```bash
uv run uvicorn app:app --app-dir 02_langgraph_workflows/02_sequential_workflows/backend
```

**4. Open the app:** navigate to `http://127.0.0.1:8000`

**5. Explore the API docs:** navigate to `http://127.0.0.1:8000/docs`

> **Note:** Do not use `--reload` on Windows. Uvicorn's reloader spawns a subprocess that may not inherit the `uv` virtual environment, causing `ModuleNotFoundError` for `langgraph` and other dependencies.

---

## 12. Key Design Decisions

| Decision | Why |
|----------|-----|
| `NotRequired` in `NoteState` | Graph invoked with partial state (`topic` only); other fields populated progressively |
| `state.get()` instead of `state[]` for optional fields | Type-safe access — `[]` would raise a type error on `NotRequired` fields |
| `load_dotenv()` at the top of `app.py` | Must run before any LLM client is created; one call at startup is cleaner than scattering it across modules |
| `Path(__file__).resolve()` for frontend path | Absolute path survives any working directory — critical when launched with `--app-dir` |
| `HTTPException(500)` wrapping workflow errors | LLM failures (rate limits, API key errors, timeouts) return a structured JSON error instead of a raw 500 traceback |
| Single `llm = get_llm()` at module level in nodes.py | One API client shared across all nodes — avoids re-initialising the client on every invocation |
| f-strings over `PromptTemplate` | No LCEL chains needed — direct state access makes f-strings simpler and equally effective |
| Relative API URL `/generate_note` in frontend | Works on any port — frontend and backend are co-served so the origin is always the same |
