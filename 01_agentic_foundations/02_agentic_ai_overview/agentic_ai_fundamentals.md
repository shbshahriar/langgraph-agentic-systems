# Agentic AI Fundamentals — Architecture, Characteristics & Core Components

> **A practical guide for LangGraph builders: understanding how agentic systems think, plan, act, and adapt**

Instead of waiting for instructions like traditional chatbots, an agentic system operates on a fundamentally different loop:

```
Goal → Plan → Execute → Observe → Adapt → Complete
```

This guide covers what Agentic AI is, its six core characteristics, the five architectural components that power it, and how all of it maps directly to LangGraph-based development.

---

## 1. What is Agentic AI?

![Agentic AI Overview](https://images.openai.com/static-rsc-4/8lwTMda6Vph9-o9m9-IUmupyHdWnQPx9dkqfcowU9-yscpolvVIT6aBfaO5IBxB_DtjXf-UMZ9Trk2uKrY67PsFNM8N3oF7OTUzwXAWISR-fkf8kiJlDrk_meLhlXjLeAfx2VA06avRGAceXegvvsXel4lRmiGJ7zA8sYARC1wa9l58eNWazcrAJ65F6LPPs?purpose=fullsize)

**Agentic AI** is a software paradigm where an AI system is assigned a goal and independently works toward achieving it — with minimal human intervention.

Unlike standard Generative AI, it does not simply respond, retrieve, or generate. It **acts strategically**.

### Execution Model Comparison

| Model | Flow |
|-------|------|
| Generative AI | `User Prompt → Model Response` |
| Agentic AI | `Goal → Plan → Execute → Observe → Adapt → Complete` |

### The Difference in Practice

**Prompt:** *"Hire a senior data analyst."*

| System | What it does |
|--------|-------------|
| Generative AI | Writes a job description |
| Agentic AI | Writes JD → posts listing → searches candidates → schedules interviews → evaluates profiles → adapts strategy if hiring fails → completes onboarding |

Same intelligence engine. Completely different behavior model.

---

## 2. Six Core Characteristics of Agentic AI

To identify whether a system is truly agentic, look for these traits.

---

### 2.1 Autonomy

![Autonomy](https://images.openai.com/static-rsc-4/LZLqieSZksATzPuPJ0YG8Kv4f36F70x4cO-2WM_4PvFud70oWRSMs7PQByCdDeG8Icf53hvCrdpSaR07wtmWBoGhJ70Uv1XoN11HLAqswWc2RRfF8AARMKTm5N8SheW_WJOU35som1dy-69a7UXrr2PK7J7iZwN1J34XuMAaEldrMZDYxufdskbLTIdWeNh1?purpose=fullsize)

Autonomy means the system executes tasks, selects tools, makes decisions, and continues workflows **without constant user instructions**.

Instead of asking:
> *"Should I send interview emails?"*

The agent sends them automatically based on its current plan and state.

---

### 2.2 Goal-Oriented Behavior

Agentic systems operate with a **persistent objective** — everything they do serves that goal.

```
Goal: "Hire a machine learning engineer"
    ↓
Subtasks auto-generated:
  ├── Create job description
  ├── Publish listing
  ├── Shortlist candidates
  ├── Schedule interviews
  └── Evaluate performance
```

The goal acts like a compass guiding every decision.

---

### 2.3 Planning Ability

![Planning](https://images.openai.com/static-rsc-4/fGKrgTLQFVGWOnlkLGR5zK55xZtu4-ZZswhyHTWy-n9ATniFDV2QsN9IQ_mzKZno0oN-LSCmxLnkrm58Ek5eKdA6vzbEdfCYNQ2yHIMS7hMdSDBfUq21ULiEHoilzegNAaIPtVKMDCnoxOkt9d_weoyENYd4WXfWreNdpgz953xK91FSY9HHPAZDmLQ9FsfE?purpose=fullsize)

Planning converts large objectives into structured, executable steps.

```
Goal: Launch hiring pipeline
    ↓
Step 1: Draft job description
Step 2: Publish listing to target platforms
Step 3: Retrieve and filter candidate pool
Step 4: Rank candidates by criteria
Step 5: Schedule and manage interviews
```

Planning is what separates a reactive chatbot from a proactive agent.

---

### 2.4 Reasoning

Reasoning enables the agent to interpret results, evaluate alternatives, and make informed decisions mid-execution.

**Example:** Candidate quality is low after initial search.

Agent reasons:
```
Current approach insufficient
  → Expand search region
  → Adjust experience requirement
  → Switch job platforms
```

This is not scripted automation — it is **intelligent decision-making**.

---

### 2.5 Adaptability

![Adaptability](https://images.openai.com/static-rsc-4/ap39-Nu5BnHJLLL7C7W1gZNmvkKnElmdQHBD508K8u8UKT1kE09pj5nSseyNWJdLL9aT_Q1P22q_hcBZ_gFxRBqgbkEUOzeu3V5QTnziHw1fk-Xw3BYdsk09k2HsmjO46ujmdgrO7-8xna1JvUfUIo8zMmm8F6I_vTiREVph5ByD1pc-nS1sbrwkg9_U2XMF?purpose=fullsize)

Agentic systems adjust dynamically when plans fail, rather than stopping.

**Scenario:** No candidates respond to outreach.

Agent response:
- Increases offered salary range
- Rewrites job posting wording
- Switches to a different hiring platform
- Targets candidates in alternative regions

Adaptability converts failure into iteration — agents don't give up, they recalibrate.

---

### 2.6 Context Awareness

Context awareness allows agents to remember previous interactions, user preferences, system constraints, and environmental signals across sessions.

**Example:** Recruiter previously indicated preference for remote candidates.

Agent automatically:
- Prioritizes remote profiles in search
- Filters out on-site-only candidates
- Adjusts sourcing strategy accordingly

This creates **continuity** — the agent behaves like a collaborator, not a stateless tool.

---

## 3. Five Core Components of an Agentic AI System

![Agent Architecture](https://images.openai.com/static-rsc-4/bZsmhe9BvucUIQYokm1XdZ4fZMLdi0Agy_qaKV5Z7wkHNBg-sH7fxJRY8MDXJcYnDpj9DzFuMwPE-2cP5DZeKGqlGdEVgAjFNdOjE6lRUvnsBIGSifVSRRwIrsRCOlesH_McF1pVrV67j_ZtrnlT-zESlt-00I4t85enXDrgN6nycoxtIjArchCei7d_Gumy?purpose=fullsize)

Most Agentic AI applications are built from five essential building blocks — the **agent stack architecture**.

---

### 3.1 Brain (LLM)

The Brain is a Large Language Model that serves as the cognitive core of the agent.

Responsibilities:
- Interpreting goals and user intent
- Planning multi-step strategies
- Reasoning through decisions
- Generating responses and tool calls
- Coordinating overall agent behavior

Examples: GPT-4o, Claude, Gemini, Llama 3

> Without the Brain, the agent cannot think.

---

### 3.2 Orchestrator

The Orchestrator controls workflow execution — it is the *conductor* of the agent system.

Responsibilities:
- Sequencing tasks in the correct order
- Routing decisions between branches
- Managing state transitions
- Handling failures and retries
- Coordinating multiple tools and agents

Common orchestrators:

| Tool | Use Case |
|------|----------|
| **LangGraph** | Stateful multi-step agent workflows |
| CrewAI | Multi-agent collaboration |
| AutoGen | Conversational multi-agent systems |
| Semantic Kernel | Enterprise agent orchestration |

**In LangGraph specifically:**
```
nodes  = actions (what happens)
edges  = transitions (what comes next)
state  = memory carrier (what persists)
```

---

### 3.3 Tools

Tools allow agents to interact with the outside world, moving beyond conversation into execution.

```
Calendar API       → schedule interviews
Email sender       → contact candidates
Database query     → retrieve company data
Search engine      → find candidates online
CRM / ATS system   → track hiring pipeline
Vector store       → retrieve knowledge
```

> Without tools, agents can only talk. With tools, agents can act.

---

### 3.4 Memory

Memory enables continuity across workflows and sessions.

#### Short-Term Memory
Stores conversation state, intermediate reasoning steps, and temporary outputs within a single run.

*LangGraph equivalent:* the `State` object passed through the graph

#### Long-Term Memory
Stores user preferences, behavioral history, domain knowledge, and embeddings that persist across runs.

*LangGraph equivalent:* vector database (Chroma, FAISS, Pinecone)

| Memory Type | Scope | Storage |
|------------|-------|---------|
| Short-term | Current session | In-memory state |
| Long-term | Across sessions | Vector / SQL database |

> Memory transforms a stateless chatbot into a persistent assistant.

---

### 3.5 Supervisor

The Supervisor ensures the agent behaves safely, correctly, and within defined boundaries.

Responsibilities:
- Enforcing guardrails and permissions
- Monitoring execution for errors
- Resolving failures and retries
- Escalating ambiguous or edge-case decisions
- Approving sensitive actions before execution

**Example:** Agent attempts to send emails to external candidates.

Supervisor validates:
- Are email permissions granted?
- Is the recipient list within approved scope?
- Has the message content been reviewed?

> The Supervisor keeps agents reliable in production environments.

---

## 4. Full Architecture — Mental Model

Here is how all five components connect in a complete agentic execution pipeline:

```
User Goal
    ↓
Brain (LLM interprets intent and plans)
    ↓
Orchestrator (routes and sequences tasks)
    ↓
Tools (executes actions in external systems)
    ↓
Memory (tracks context and state)
    ↓
Supervisor (validates safety and correctness)
    ↓
Goal Completion
```

Each layer is independent but they work together as an integrated system. Failure in one layer (e.g., tool error) is handled by the orchestrator, which uses the brain's reasoning and memory context to adapt.

---

## 5. Mapping Agentic Components to LangGraph

If you're building with LangGraph, every concept above maps directly to implementation constructs:

| Agentic Component | LangGraph Equivalent |
|------------------|---------------------|
| Brain (LLM) | LLM node (`ChatModel` invocation) |
| Planning | Conditional edges (`should_continue`, routing logic) |
| Tools | `ToolNode`, custom tool functions |
| Short-term memory | `State` TypedDict passed through graph |
| Long-term memory | Vector store retriever node |
| Orchestrator | `StateGraph` engine |
| Supervisor | Guardrail node, human-in-the-loop interrupt |

LangGraph exists specifically to support **agentic execution patterns** — stateful, multi-step, conditional workflows — not simple prompt-response chains.

The shift from chatbot to agent is primarily about **adding orchestration layers strategically**.

---

## Summary

| Characteristic | What it enables |
|---------------|----------------|
| Autonomy | Acts without constant prompting |
| Goal-orientation | Pursues persistent objectives |
| Planning | Decomposes goals into steps |
| Reasoning | Makes informed decisions mid-task |
| Adaptability | Recovers and iterates on failure |
| Context awareness | Maintains continuity across sessions |

| Component | Role |
|-----------|------|
| Brain (LLM) | Cognitive core — thinks and plans |
| Orchestrator | Controls workflow execution flow |
| Tools | Connects agent to the real world |
| Memory | Persists state and knowledge |
| Supervisor | Ensures safe and correct behavior |

> Agentic AI is not a smarter chatbot — it is a different class of system built to pursue goals, not answer questions.
