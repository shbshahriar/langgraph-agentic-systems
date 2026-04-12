# LangGraph Core Concepts — Workflow Patterns, State Management & Execution Model

> **The mental model you need before writing serious LangGraph agents: graph structure, state, reducers, workflow patterns, and how execution actually works under the hood**

LangGraph is an orchestration framework for building **multi-step, stateful, agentic AI workflows** using graph-based execution instead of linear chains. Instead of fragile step-by-step pipelines, LangGraph lets you design adaptive workflows with conditional routing, parallel execution, iterative refinement loops, and modular agent systems.

---

## Core Mental Model

```
Nodes  = tasks (functions, LLM calls, tools)
Edges  = transitions between tasks
State  = shared memory flowing across all nodes
```

---

## Table of Contents

1. [What Is LangGraph?](#1-what-is-langgraph)
2. [Common Workflow Design Patterns](#2-common-workflow-design-patterns)
3. [Graph Structure — Nodes and Edges](#3-graph-structure--nodes-and-edges)
4. [State Management](#4-state-management)
5. [Reducers — How State Updates Work](#5-reducers--how-state-updates-work)
6. [Execution Model](#6-execution-model)
7. [Concept-to-System Mapping](#7-concept-to-system-mapping)

---

## 1. What Is LangGraph?

![LangGraph Overview](https://images.openai.com/static-rsc-4/WN4p0-dmHjkBK2j0-6TAyw1vhqInn5_3ayHdrlUUGm-f-EsvSw0eJJMpzasXaSnQU8nUM1B_-10MkYDNwGWYd2QXNDvl3pbpyFIT9zs7BHrbsHsl8_XBhxA9s4acwAg1NYZkE3Buyv5-Slc0gIfa632RKOpCY9AWBYkjDc9ucYjY2XMb0Clui_qpNwZlV4Rk?purpose=fullsize)

LangGraph models AI workflows as **graphs** rather than sequential chains.

**Example workflow:**
```
User Query
    ↓
Analyze Intent
    ↓
Route Task
    ↓
Call Tool  OR  Retrieve Context
    ↓
Generate Response
```

Unlike traditional pipelines, graphs natively support:

| Capability | What it enables |
|-----------|----------------|
| Branching | Different paths based on conditions |
| Looping | Repeat steps until a quality threshold is met |
| Retries | Recover from failures without restarting |
| Parallel steps | Run independent nodes simultaneously |
| Interruptions | Pause for human approval mid-workflow |

> LangGraph is the **control system for agent behavior** — it turns fragile pipelines into intelligent, adaptive workflows.

---

## 2. Common Workflow Design Patterns

![Workflow Patterns](https://images.openai.com/static-rsc-4/_6S0Z626KDm2HkUOKn9ZUH4ExzN66UHpcvuXn-9pKsYt6zpgRWHIZD3hGLWMze9Trr8l0y9kwUMlDGIhrSHsYrW6SCwNTkJ7ofs1qsEIx3O_JruaramM7RqDIhk9_QFoW2hhA_J1E01LCdTg5dRhD2JR_lM2OJW3Ir4rIYLKpsjXS3oidpouyMs72mxMk6Br?purpose=fullsize)

LangGraph supports five foundational workflow patterns. Understanding them gives you a vocabulary for designing agent systems.

---

### 2.1 Prompt Chaining

Break complex tasks into smaller sequential steps where each output feeds the next.

```
User Input → Summarize Document → Extract Insights → Generate Report
```

**Best used when:**
- Tasks are inherently sequential
- Output of step A is direct input to step B
- You want to reduce cognitive load on the model by isolating each concern

---

### 2.2 Routing

Classify input and dynamically select an execution path.

```
User Query
    ↓
Classify Intent
    ↓
Finance Query → Finance Agent
HR Query      → HR Agent
Tech Query    → Tech Agent
```

Routing enables **specialization** inside agent systems — each agent handles its domain without being overloaded with context from others. Especially powerful for hybrid pipelines (RAG router + Pandas agent, etc.).

---

### 2.3 Parallelization

Run independent steps simultaneously and merge results.

```
User Input
    ↓
┌──────────────┬──────────────┬────────────────┐
Retrieve Docs  Analyze Sentiment  Extract Keywords
└──────────────┴──────────────┴────────────────┘
    ↓
Merge Results → Generate Response
```

**Benefits:**
- Faster end-to-end execution
- Richer, multi-dimensional outputs
- Horizontally scalable pipelines

---

### 2.4 Orchestrator–Workers Pattern

![Orchestrator-Workers](https://images.openai.com/static-rsc-4/5bePzaysT9Wn6l3TmdgOvG5K2cM2u2vOXXEiKSJ4PdV7ZM5FcEZEPiWDQ07q6Oe6dljE5IzYjyK1oyDk7kUsNscAJ8SbygG_O6l8WAxM3sApZiPzs0m574OnQIawse_SRC3536UoEuKEZ-CwI6aTGfC_7c4kQAF1TSi3SS7VU1iCfh9CfP9IL8q1o0P-ml9M?purpose=fullsize)

A central orchestrator agent decomposes a goal and delegates to specialized worker agents.

```
Orchestrator (receives goal, plans work)
    ↓
┌──────────────┬──────────────┬─────────────────┐
Research Agent  Coding Agent  Writing Agent  Evaluator Agent
└──────────────┴──────────────┴─────────────────┘
    ↓
Synthesize outputs → Final Result
```

Each worker solves a focused, bounded problem. This pattern is the backbone of **multi-agent architectures**.

---

### 2.5 Evaluator–Optimizer Pattern

![Evaluator-Optimizer](https://images.openai.com/static-rsc-4/VAdto8uEsXwdhNJApTcpRq2qm0gSYu0gDAaHtd2xFXelxRtcemD5EJinQOQsquJmC4eYmMecv2GpCTQDAxHKmwKc2xmLguZnlQbBeMufMxYXVnRSQrKLlIsOUSBvVoGk0vIQ1rbdZ5mxSk51VL_jE7UFPsnVm4c5SGLg21RPjdz0DmbXufNexV92b1ff6Ynm?purpose=fullsize)

One model generates output; another evaluates and drives iterative improvement.

```
Generate Answer
    ↓
Evaluate Quality
    ↓
Pass threshold? → YES → Final Output
                → NO  → Improve Answer → (loop back)
```

**Best used for:**
- Complex reasoning tasks
- Code generation and debugging
- Essay or report refinement
- Research synthesis with quality requirements

---

## 3. Graph Structure — Nodes and Edges

![Graph Structure](https://images.openai.com/static-rsc-4/BhQ4_MiQUMSZBaB-dtm_GDGuo9hYE9fOGxqUGzZGEVKJWUyf5PDDShxzuzrRJtiynz_9EFKA4yhuEmGjR7SVt7AxZwqxJh15R-g0M-vc2S-3GsGfbFJSUPF5noTNuis6U4vGzcMYsDN0kGtZFrmM1zG47cmLGx6KCnZ16frqB52h3DsKQ3fpLSwcdZczFuUK?purpose=fullsize)

LangGraph workflows are built from two primitive components: **nodes** and **edges**.

---

### Nodes

A node is a discrete execution step — any callable that reads state, performs work, and returns updated state.

**Examples of what a node can be:**
- LLM call
- Tool invocation (API, database query)
- Retrieval step (vector search)
- Classifier or router
- Planner or decomposer
- Evaluator or quality checker

```python
def generate_summary(state: AgentState) -> AgentState:
    # read from state
    # perform LLM call
    # update state
    return updated_state
```

**Every node follows the same contract:**
1. Read from state
2. Do work
3. Return updated state

---

### Edges

Edges define how execution flows between nodes.

```
Summarize → Evaluate
Evaluate  → Improve   (if quality low)
Evaluate  → Output    (if quality acceptable)
Improve   → Evaluate  (loop back)
```

**Types of edges:**

| Edge Type | Behavior |
|-----------|---------|
| Direct edge | Always transition from A to B |
| Conditional edge | Choose path based on state value |
| Loop edge | Return to an earlier node |
| Terminal edge | Route to `END` to finish execution |

Edges are what transform a simple pipeline into an intelligent system capable of routing, looping, and retrying.

---

## 4. State Management

![State Management](https://images.openai.com/static-rsc-4/MgUscuEK_UULajNFuCquNAjl8zwS2K2h0CsF5-N1Q_ewCbz1w2R_p2HG-M4kI6kCMOfyFYFaZ2tMOngZKkpqsvJd4_bu-QNClymBwCOhpPk0kcwa58Kbne8MwOxe42zBtjOKCXj2_i1u4WJ9KXzYQHXstQVpbvGM_W0uC5j3IOHy9UeIcMOyot8nD6EhVShD?purpose=fullsize)

State is the **shared memory** that flows through every node in the graph. It is the single source of truth for the entire workflow execution.

**Example state object:**
```python
from typing import TypedDict, List

class AgentState(TypedDict):
    query: str
    documents: List[str]
    summary: str
    quality_score: float
    final_answer: str
    retry_count: int
```

Every node can read any field and update any field. The updated state is passed to the next node automatically.

### Why State is Central

| Without State | With State |
|--------------|-----------|
| Each node is isolated | Nodes share context |
| Agent forgets prior steps | Agent builds on prior work |
| No adaptive behavior | Decisions informed by history |
| Pipelines only | Full agent workflows |

State is what allows an agent to know *where it is*, *what it has done*, and *what context should influence the next step*. Without it, you have a chatbot. With it, you have an agent.

---

## 5. Reducers — How State Updates Work

![Reducers](https://images.openai.com/static-rsc-4/pYYOLbL62ioWTL_Bb8e6yNJbWPVRhJwRHSA-3109Uh5GhaFhLEomsSBf-2FEBT8YRan8mkG67ItZyojdJRkelH-YAPDMpf-4xJupJK68wY4BtiPAEIQFqC73-zSTsrFh92BAwi22olpX8pvqbQGY7hXSofKuD-jL1qTKa_aFj27tjFqln_79O2e3iEFd2_9u?purpose=fullsize)

Reducers control **how state updates are applied** when multiple nodes modify the same field — especially critical in parallel execution where conflicts can occur.

Three strategies:

---

### Replace Strategy

New value fully overwrites the existing value.

```python
state["summary"] = new_summary  # replaces previous summary
```

**Use when:** Only the latest result is relevant (e.g., a refined answer replacing a draft).

---

### Append Strategy

New values are added to the existing collection.

```python
state["documents"] += retrieved_docs  # accumulates evidence
```

**Use when:** Building up a collection progressively across multiple retrieval steps.

---

### Merge Strategy

Multiple partial updates are combined into a unified structure.

```python
state["analysis"].update(new_partial_analysis)
```

**Use when:** Multiple parallel nodes each contribute to the same composite output.

### Why Reducers Matter

In parallel execution, two nodes might update the same state field at the same time. Without reducers, one update would silently overwrite the other. Reducers define the merge contract upfront, making parallel workflows safe and predictable.

---

## 6. Execution Model

![Execution Model](https://images.openai.com/static-rsc-4/EPHxF4PZu5HOi5PsIz_GgXLLyfVr-3TNbeKE3HIIfZ9qHDb3-UjWLdrSOyeYpzau9DVFVzSudPl3rc_xG1Uu3EB7Wygktm_Ui67BFLMau9Aqo7bJIavQggD22v_-Qag6zgjR0-ZYVe7PTvkBX-Mc1BmZk-LirWfYdbp-jbe0WFrZZgr8kqJvjzBQE817w5aP?purpose=fullsize)

Understanding LangGraph's execution model makes debugging significantly easier. Execution happens in three structured stages.

---

### Stage 1 — Graph Compilation

Before any execution begins, LangGraph compiles the workflow definition.

**What it checks:**
- All nodes are connected (no orphaned nodes)
- All edges reference valid nodes
- Entry point and terminal nodes are defined
- No structural inconsistencies

Think of compilation as **type-checking for your workflow** — it catches structural errors before a single LLM call is made.

---

### Stage 2 — Message Passing Between Nodes

During execution, nodes communicate through state updates — not direct function calls.

```
Node A executes → updates state["field_x"]
    ↓
Node B reads state["field_x"]
    ↓
Node C reacts to both state["field_x"] and state["field_y"]
```

No node directly calls another. They all read from and write to the shared state. This decoupling is what makes the graph so flexible — you can rewire execution flow by changing edges without touching node implementations.

---

### Stage 3 — Supersteps

LangGraph executes workflows in **supersteps** — a concept borrowed from distributed computing.

**A superstep means:**
1. All nodes that are currently eligible to run execute simultaneously
2. All state updates from that round are collected
3. Reducers apply the updates to produce the new state
4. The next round of eligible nodes is determined

```
Superstep 1:
  ├── Retrieve Docs (runs)
  └── Classify Intent (runs)
      ↓ (state merged)

Superstep 2:
  ├── Generate Answer (runs, uses retrieved docs + intent)
  └── Evaluate Confidence (runs)
      ↓ (state merged)

Superstep 3:
  └── Final Output or Loop Back
```

Supersteps are why LangGraph can run parallel nodes safely without state corruption — all writes within a superstep are collected before any reads happen in the next superstep.

---

## 7. Concept-to-System Mapping

For real production agent workflows, every concept in this guide maps to a concrete design decision:

| Concept | Role in Real Systems | LangGraph Implementation |
|---------|---------------------|--------------------------|
| Prompt chaining | Multi-step reasoning pipelines | Sequential node chain |
| Routing | Hybrid agent selection, model dispatch | Conditional edges |
| Parallelization | Performance scaling, multi-source retrieval | Parallel node branches |
| Orchestrator–workers | Multi-agent collaboration | Subgraph nodes |
| Evaluator–optimizer | Output quality refinement | Loop edges with condition |
| State | Workflow memory, context continuity | `TypedDict` state schema |
| Reducers | Conflict-safe parallel updates | `Annotated` field reducers |
| Supersteps | Safe concurrency, predictable ordering | Built-in graph engine behavior |

---

## Summary

```
LangGraph = Nodes + Edges + State + Reducers + Execution Engine
```

| Layer | What it gives you |
|-------|------------------|
| Nodes | Modular, composable execution steps |
| Edges | Routing, branching, looping, retrying |
| State | Shared memory across the entire workflow |
| Reducers | Safe, conflict-free state updates in parallel |
| Supersteps | Deterministic concurrent execution |

> LangChain helps you *call* models.
> LangGraph helps you *coordinate* intelligence.
