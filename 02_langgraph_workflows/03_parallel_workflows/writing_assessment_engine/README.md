# Parallel Writing Assessment Engine (PWAE)

A production-grade parallel LLM pipeline built with LangGraph that evaluates written content across 8 linguistic dimensions simultaneously and generates structured improvement feedback.

---

## What This System Does

PWAE takes a piece of writing — paragraph, essay, or article — runs 9 independent LLM evaluations in parallel, merges all results, and produces a structured report with scores, argument analysis, and an AI-generated revision plan.

**Key capabilities:**

- Detects writing format automatically (no LLM required for classification)
- Runs 9 evaluator nodes concurrently using LangGraph fan-out
- Uses reducer-based state merging to safely handle concurrent writes
- Forces structured JSON output from Claude via Pydantic + tool calling
- Computes a weighted final score from 8 dimension scores
- Generates a 5-field improvement report using a single feedback LLM call

---

## Architecture

```
START
  │
  ▼
format_classifier_node          ← keyword heuristic, no LLM
  │
  ├── grammar_evaluator_node ──────────────────────────────────┐
  ├── clarity_evaluator_node ─────────────────────────────────┤
  ├── coherence_evaluator_node ──────────────────────────────┤
  ├── depth_evaluator_node ─────────────────────────────────┤
  ├── structure_evaluator_node ────────────────────────────── ┤  (parallel — 9 nodes)
  ├── vocabulary_evaluator_node ───────────────────────────── ┤
  ├── tone_evaluator_node ─────────────────────────────────── ┤
  ├── readability_evaluator_node ──────────────────────────── ┤
  └── argument_structure_node ─────────────────────────────── ┘
                                                               │
                                                               ▼
                                                  evaluation_merger_node   ← no LLM
                                                               │
                                                               ▼
                                                  feedback_generator_node  ← LLM
                                                               │
                                                               ▼
                                                              END
```

**Fan-out:** `format_classifier` connects to all 9 nodes — LangGraph launches them all simultaneously in separate threads.

**Fan-in:** All 9 nodes connect to `evaluation_merger` — LangGraph waits for every node to finish before proceeding.

---

## Folder Structure

```
writing_assessment_engine/
│
├── backend/
│   ├── app.py          FastAPI server — serves frontend + API from one process
│   ├── workflow.py     LangGraph graph definition — wires all 11 nodes
│   ├── nodes.py        All 11 node functions across 5 stages
│   ├── state.py        WritingState TypedDict + inline reducers
│   ├── schemas.py      Pydantic models for LLM output + API request/response
│   ├── reducers.py     Named reducer functions used by evaluation_merger_node
│   ├── router.py       Format classification logic (keyword scoring heuristic)
│   ├── llm.py          Claude LLM factory — get_llm() returns ChatAnthropic
│   ├── prompts.py      One prompt function per evaluator node
│   └── config.py       Central config — model name, score weights, format keywords
│
├── frontend/
│   ├── index.html      UI — text input panel + evaluation results dashboard
│   ├── main.js         Fetch logic, score rendering, feedback display
│   └── style.css       Styling
│
├── notebook/
│   └── parallel_llm_demo.ipynb   Jupyter walkthrough of the graph execution
│
├── sample_texts.txt    Example paragraph, essay, and article inputs for testing
└── README.md
```

---

## Pipeline Stages

### Stage 1 — Format Classifier (1 node, no LLM)

**Node:** `format_classifier_node`  
**File:** `nodes.py` → calls `classify_format()` from `router.py`

Detects writing format using a 3-step heuristic — no LLM involved:

1. **Word count gate** — texts under 30 words are always `"paragraph"`
2. **Keyword scoring** — counts essay keywords (thesis, furthermore, in conclusion...) vs article keywords (according to, study shows, researchers...)
3. **Decision with word count guard** — highest keyword score wins, but must meet minimum word count threshold

| Format | Min words | Max words |
|---|---|---|
| paragraph | 30 | 100 |
| essay | 150 | 1000 |
| article | 120 | 500 |

Output: `format_type` field in state (`"paragraph"`, `"essay"`, or `"article"`)

---

### Stage 2 — Parallel LLM Evaluators (8 nodes, concurrent)

All 8 nodes follow the same 3-step pattern:

```python
structured_llm = get_llm().with_structured_output(ScoreOutput)
result = structured_llm.invoke(dimension_prompt(state["text"]))
return {"dimension_score": result.score}
```

`with_structured_output(ScoreOutput)` forces Claude to respond via tool calling — it cannot return free text. The result is a typed `ScoreOutput` object with guaranteed `score: float` and `reason: str` fields.

| Node | Evaluates | Output field |
|---|---|---|
| `grammar_evaluator_node` | Spelling, punctuation, subject-verb agreement, tense | `grammar_score` |
| `clarity_evaluator_node` | Ease of understanding, ambiguous phrasing, jargon | `clarity_score` |
| `coherence_evaluator_node` | Logical flow, transitions, paragraph linking | `coherence_score` |
| `depth_evaluator_node` | Topic thoroughness, examples, evidence, nuance | `depth_score` |
| `structure_evaluator_node` | Intro/body/conclusion presence, logical ordering | `structure_score` |
| `vocabulary_evaluator_node` | Word variety, precision, avoidance of repetition | `vocabulary_score` |
| `tone_evaluator_node` | Formality, voice consistency, audience alignment | `tone_score` |
| `readability_evaluator_node` | Sentence length variation, passive voice, lexical density | `readability_score` |

All scores are floats on a 0–10 scale.

---

### Stage 3 — Argument Structure Analysis (1 node, concurrent with Stage 2)

**Node:** `argument_structure_node`

Runs in parallel with the 8 evaluator nodes. Uses `ArgumentOutput` (5 categorical fields) instead of `ScoreOutput`.

| Field | Type | Values |
|---|---|---|
| `claim_presence` | bool | True / False |
| `supporting_evidence` | str | none / weak / moderate / strong |
| `reasoning_quality` | str | poor / fair / good / excellent |
| `counterargument_usage` | bool | True / False |
| `critical_thinking_depth` | str | surface / moderate / deep |

Output written to `argument_analysis` dict in state.

---

### Stage 4 — Evaluation Merger (1 node, no LLM)

**Node:** `evaluation_merger_node`

Runs after all 9 parallel nodes complete. Groups the 8 individual scores into a structured breakdown and computes the weighted final score.

**Dimension breakdown structure:**

```json
{
  "language":    {"grammar": 7.5, "clarity": 8.0, "vocabulary": 7.0, "tone": 7.5},
  "structure":   {"structure": 8.0, "coherence": 7.5, "depth": 6.5},
  "argument":    {"claim_presence": true, "supporting_evidence": "moderate", ...},
  "readability": 7.0
}
```

**Score weights (from `config.py`):**

| Dimension | Weight | Rationale |
|---|---|---|
| grammar | 0.15 | Universally critical |
| clarity | 0.15 | Universally critical |
| coherence | 0.15 | Bridges all sections |
| readability | 0.15 | Reading ease baseline |
| depth | 0.10 | Format-dependent |
| structure | 0.10 | Format-dependent |
| vocabulary | 0.10 | Format-dependent |
| tone | 0.10 | Format-dependent |

**Formula:** `final_score = Σ(score[dim] × weight[dim])`  All weights sum to exactly 1.0.

---

### Stage 5 — Feedback Generator (1 node, LLM)

**Node:** `feedback_generator_node`

The final node. Receives the fully populated state — all 8 scores, format type, and original text — and produces a structured `FeedbackOutput` via Claude.

| Field | Type | Description |
|---|---|---|
| `strengths` | List[str] | 3 specific writing strengths with text references |
| `weaknesses` | List[str] | 3 specific areas needing improvement |
| `revision_plan` | List[str] | 3 actionable revision steps addressing each weakness |
| `recommended_style_adjustments` | List[str] | 2 concrete style changes |
| `target_band_prediction` | str | `"Band X–Y: <one-sentence justification>"` |

---

## State Design

**File:** `backend/state.py`

`WritingState` is a `TypedDict` — LangGraph's required state format. Every field uses `Annotated[type, reducer_fn]` to define how concurrent writes are merged.

**Two inline reducers:**

| Reducer | Used for | Behaviour |
|---|---|---|
| `_take_new(old, new)` | Float scores, strings | Always returns the new value |
| `_merge_dicts(old, new)` | `argument_analysis`, `feedback_report`, `dimension_breakdown` | Merges dicts — new keys win on conflict |

Without reducers, parallel nodes writing to the same state field would cause the last write to silently overwrite earlier ones. Reducers make concurrent writes safe and deterministic.

---

## Reducer Design

**File:** `backend/reducers.py`

Four named reducers used explicitly inside `evaluation_merger_node` to group scores by category before writing back to state:

| Function | Groups |
|---|---|
| `merge_language_scores` | grammar, clarity, vocabulary, tone |
| `merge_structure_scores` | structure, coherence, depth |
| `merge_argument_scores` | all 5 argument analysis fields |
| `merge_final_evaluation` | final_score + dimension_breakdown |

These are distinct from the inline state reducers — they perform logical grouping, not concurrent-write conflict resolution.

---

## Pydantic Schemas

**File:** `backend/schemas.py`

**LLM output schemas** (used with `with_structured_output()`):

| Schema | Used by | Fields |
|---|---|---|
| `ScoreOutput` | 8 evaluator nodes | `score: float`, `reason: str` |
| `ArgumentOutput` | `argument_structure_node` | 5 categorical fields |
| `FeedbackOutput` | `feedback_generator_node` | 5 list/string fields |

**API schemas** (used by FastAPI):

| Schema | Used by | Purpose |
|---|---|---|
| `WritingRequest` | POST /evaluate-writing | Validates input text (min 10 chars) |
| `WritingResponse` | POST /evaluate-writing | Shapes JSON response to frontend |

---

## API

**Base URL:** `http://localhost:8000`

### `POST /evaluate-writing`

**Request body:**
```json
{
  "text": "Your writing here..."
}
```

**Response:**
```json
{
  "format_type": "essay",
  "dimension_scores": {
    "language":    {"grammar": 7.5, "clarity": 8.0, "vocabulary": 7.0, "tone": 7.5},
    "structure":   {"structure": 8.0, "coherence": 7.5, "depth": 6.5},
    "argument":    {"claim_presence": true, "supporting_evidence": "moderate",
                    "reasoning_quality": "good", "counterargument_usage": false,
                    "critical_thinking_depth": "moderate"},
    "readability": 7.0
  },
  "argument_analysis": {
    "claim_presence": true,
    "supporting_evidence": "moderate",
    "reasoning_quality": "good",
    "counterargument_usage": false,
    "critical_thinking_depth": "moderate"
  },
  "final_score": 7.58,
  "feedback_report": {
    "strengths": ["...", "...", "..."],
    "weaknesses": ["...", "...", "..."],
    "revision_plan": ["...", "...", "..."],
    "recommended_style_adjustments": ["...", "..."],
    "target_band_prediction": "Band 7–8: ..."
  },
  "error": null
}
```

### `GET /health`

Returns `{"status": "ok"}`.

### `GET /docs`

Interactive Swagger UI for testing all endpoints.

---

## Configuration

All settings live in `backend/config.py` — one file controls the entire system:

| Constant | Value | Purpose |
|---|---|---|
| `MODEL_NAME` | `claude-haiku-4-5-20251001` | Fastest Claude model — ideal for 9 parallel calls |
| `TEMPERATURE` | `0.3` | Slightly flexible but mostly consistent for scoring |
| `SCORE_WEIGHTS` | dict | Per-dimension weights summing to 1.0 |
| `FORMAT_KEYWORDS` | dict | Essay and article keyword lists for format detection |
| `FORMAT_MIN_WORDS` | dict | Minimum word counts per format |
| `FORMAT_MAX_WORDS` | dict | Maximum word counts per format |

---

## How to Run

**Requirements:** Python 3.11+, `ANTHROPIC_API_KEY` in a `.env` file

```bash
# Install dependencies
uv add fastapi uvicorn langgraph langchain-anthropic pydantic python-dotenv

# Start the server
cd writing_assessment_engine/backend
uvicorn app:app --reload --port 8000
```

Open `http://localhost:8000` in your browser.

**Important:** `load_dotenv()` runs at the top of `app.py` before any LangGraph imports. This order is required because `workflow.py → nodes.py → llm.py` reads `ANTHROPIC_API_KEY` from environment on import.

---

## LangGraph Concepts Demonstrated

| Concept | Where used |
|---|---|
| `StateGraph` with `TypedDict` | `workflow.py`, `state.py` |
| `Annotated` fields with reducer functions | `state.py` |
| Fan-out (one → many parallel edges) | `workflow.py` — `format_classifier` to 9 nodes |
| Fan-in (many → one edge) | `workflow.py` — 9 nodes to `evaluation_merger` |
| `with_structured_output()` for guaranteed JSON | `nodes.py` — all LLM nodes |
| `START` / `END` sentinels | `workflow.py` |
| `graph.compile()` and `graph.invoke()` | `workflow.py`, `app.py` |
