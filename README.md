# Agent With Tools

**Local agentic search (ReAct pattern)** — a local-first, high-performance search agent built with **LangGraph** and **Ollama**. This project demonstrates a ReAct (Reasoning + Acting) implementation that lets an LLM autonomously navigate web search and tool calls to answer complex, real-time queries.

---

## Key Features

- **State Machine architecture** for non-deterministic agent flows  
- **Cyclic graph reflection** to iteratively refine queries when tool outputs are insufficient  
- **Decoupled tool registry**: modular plugins under `src/tools/` for easy extension  
- **Local-first inference** using Ollama (Llama 3.2 3b) for zero data egress and low latency  
- **Production-grade observability** via LangSmith tracing

---

## Architecture & Design Decisions

### 1. State Management (LangGraph)
- **Cyclic Graphs**  
  Enables the agent to loop back and re-evaluate tool outputs, supporting iterative refinement rather than a single linear pass.

- **Reducer Patterns**  
  Uses `add_messages` style reducers to manage conversation state and memory buffers without manual list manipulation.

### 2. Decoupled Tool Registry
- **Separation of Concerns**  
  Tools live in `src/tools/` as modular plugins. Adding capabilities (SQL execution, File I/O, etc.) does not require changing core orchestration.

- **Schema Introspection**  
  Uses `@tool`-style decorators to auto-generate JSON schemas and enforce strict contracts between the LLM and execution environment.

### 3. Local-First Inference
- **Ollama Integration**  
  Optimized for Llama 3.2 (3b) to leverage native tool-calling fine-tuning. This provides advanced orchestration logic with no external data egress and minimal latency.

---

## Tech Stack

- **Orchestration:** LangGraph  
- **LLM Provider:** Ollama (Llama 3.2:3b)  
- **Search Engine:** DuckDuckGo (via langchain-community)  
- **Environment:** Python 3.11+  
- **Observability:** LangSmith (OpenTelemetry-compatible tracing)

## Future Roadmap
- **Dockerize:** Get this runnable for external demos
- **Hosting:** Yep, needs it. (add it to my current herku acct?)
- **UI:** Add a nextJS or reactJS front end.
- **Guardrails & Safety:** Yes, do this :-). Currently the graph is configured with a maximum recursion limit to prevent infinite tool-calling loops.
- **Testing & Evals:** Need to add.
- **Persistent Checkpointing:** Add a SQLite backend to LangGraph to allow "resuming" interrupted agent sessions.
- **Multi-Agent Orchestration:** Implementing a "Supervisor" pattern to delegate between specialized search and specialized code-execution agents.
- **Agents/Tools:** Add another agent. Add MCP(s). - Specifically for my mongoDB vector index db instance.
- **Hybrid RAG:** Consider merging this with my currnet RAG app?
