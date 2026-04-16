# AI Feedback Triage Agent

A LangGraph-based conditional workflow that ingests a raw user review and produces a structured triage decision plus a tailored response. It demonstrates production-style customer-feedback automation: sentiment detection, structured issue diagnosis, urgency-to-priority mapping, automatic escalation, and context-aware reply generation — all routed dynamically through a graph of specialized nodes.

---

## What it does

For every incoming review the agent:

1. Classifies sentiment (positive / neutral / negative) with confidence + reasoning.
2. For negative reviews, runs a structured diagnosis (issue type, tone, urgency, owning department, one-line summary).
3. Maps urgency to a ticket priority (`critical → P0`, `high → P1`, `medium → P2`, `low → P3`).
4. Flags `P0` tickets for escalation.
5. Generates a final user-facing reply through one of four specialized response writers.

Positive and neutral reviews short-circuit straight to a thank-you / acknowledgement. Negative reviews flow through the full diagnose → prioritize → escalate → respond path.

---

## Architecture

```
START
  │
  ▼
sentiment_node
  │
  ▼
sentiment_router ──► positive ─► appreciation_response ─► END
                  ─► neutral  ─► neutral_response      ─► END
                  ─► negative
                          │
                          ▼
                   diagnosis_node
                          │
                          ▼
                   priority_node
                          │
                          ▼
                  escalation_node
                          │
                          ▼
                  priority_router ─► P0 (escalated) ─► escalation_response ─► END
                                  ─► P1 / P2 / P3   ─► support_response    ─► END
```

### Folder layout

```
ai-feedback-triage-agent/
├── app/
│   ├── graph.py              # LangGraph assembly
│   ├── state.py              # ReviewState (TypedDict)
│   ├── routers.py            # sentiment_router, priority_router
│   ├── nodes/
│   │   ├── sentiment_node.py
│   │   ├── diagnosis_node.py
│   │   ├── priority_node.py
│   │   ├── escalation_node.py
│   │   └── response_nodes.py
│   └── schemas/
│       ├── sentiment_schema.py
│       └── diagnosis_schema.py
├── services/
│   └── llm_service.py        # ChatAnthropic factory
├── config/
│   └── settings.py           # model, temperature, urgency map
├── examples/
│   └── sample_reviews.json
├── tests/
│   └── test_pipeline.py
├── main.py
├── requirements.txt
└── plan.md
```

---

## Key design choices

- **Structured outputs everywhere.** Sentiment and diagnosis nodes use `with_structured_output(<Pydantic schema>)` so downstream routers can branch on `Literal` fields with no parsing or fuzzy matching.
- **Schemas embedded in shared state.** `ReviewState` stores the full `SentimentOutput` and `DiagnosisOutput` Pydantic objects — the allowed value lists live in one place (the schemas), not duplicated across the state.
- **Routers are pure functions.** `sentiment_router` and `priority_router` only read state and return a string — easy to unit-test without the LLM.
- **LLM is created lazily.** `get_llm()` is called per node so `dotenv` has loaded credentials before any client is constructed.
- **Escalation as its own node.** `escalation_node` sets `escalation_flag` based on priority; the router then branches on the flag instead of re-deriving the rule.

---

## Setup

```bash
# from repo root, using uv
uv add langgraph langchain-anthropic pydantic python-dotenv pytest
```

Create a `.env` at the repo root (or export the variable directly):

```
ANTHROPIC_API_KEY=sk-ant-...
```

Model and tuning knobs live in [config/settings.py](config/settings.py):

```python
MODEL_NAME = "claude-haiku-4-5"
TEMPERATURE = 0.2
TIMEOUT_SECONDS = 60
```

---

## Run

From inside the project directory:

```bash
python main.py
```

This loads [examples/sample_reviews.json](examples/sample_reviews.json) and prints the full triage trace for each review (sentiment → diagnosis → priority → escalation flag → generated response).

### Programmatic use

```python
from app.graph import build_graph

graph = build_graph()
result = graph.invoke({"review": "Checkout crashes when I apply a discount code."})

print(result["sentiment"].sentiment)        # "negative"
print(result["diagnosis"].issue_type)        # "bug"
print(result["priority"])                    # "P1"
print(result["escalation_flag"])             # False
print(result["response"])                    # generated reply
```

---

## Tests

Pure-logic tests for routers and priority/escalation nodes — no LLM calls required:

```bash
pytest tests/
```

Covers:

- sentiment routing (positive / neutral / negative branches)
- priority routing (escalated vs support)
- urgency → priority mapping (critical/high/medium/low → P0/P1/P2/P3)
- escalation flag (P0 sets it, others don't)

---

## Extending it

- **New department / issue type:** add the literal to [app/schemas/diagnosis_schema.py](app/schemas/diagnosis_schema.py) — routers and prompts pick it up automatically.
- **New response template:** add a function to [app/nodes/response_nodes.py](app/nodes/response_nodes.py), register it as a node in [app/graph.py](app/graph.py), and update the relevant router branch.
- **Different LLM provider:** swap [services/llm_service.py](services/llm_service.py); the rest of the graph is provider-agnostic as long as `with_structured_output` is supported.
