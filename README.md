# agentWithTools
Agent With Tools

🌐 Local Agentic Search (ReAct Pattern)
A high-performance, local-first search agent built with LangGraph and Ollama. This project demonstrates an implementation of the ReAct (Reasoning + Acting) pattern, allowing a Large Language Model (LLM) to navigate the web autonomously to answer complex, real-time queries.

🏗️ Architecture & Design Decisions
Unlike simple linear chains, this project utilizes a State Machine architecture to handle the non-deterministic nature of AI agents.

1. State Management (LangGraph)
Cyclic Graphs: Uses a cyclic graph to allow the agent to "reflect" on tool outputs. If the initial search results are insufficient, the agent can loop back and refine its query.

Reducer Patterns: Implements add_messages to manage conversation state, ensuring a robust memory buffer without manual list manipulation.

2. Decoupled Tool Registry
Separation of Concerns: Tools are isolated from the orchestration logic. The src/tools/ directory acts as a modular plugin system, making it trivial to add new capabilities (e.g., SQL execution, File I/O) without modifying the core agent.

Schema Introspection: Leverages LangChain’s @tool decorators for automatic JSON schema generation, ensuring strict contract adherence between the LLM and the execution environment.

3. Local-First Inference
Ollama Integration: Optimized for Llama 3.2 (3B). This model was chosen for its native tool-calling fine-tuning, providing GPT-4 level orchestration logic with zero data egress and minimal latency.

🛠️ Tech Stack
Orchestration: LangGraph

LLM Provider: Ollama (Llama 3.2:3b)

Search Engine: DuckDuckGo (via langchain-community)

Environment: Python 3.11+

Observability: LangSmith (OpenTelemetry-compatible tracing)

🚀 Getting Started
Prerequisites
Install Ollama: ollama.com

Pull the Model:

Bash
ollama pull llama3.2:3b
Installation
Bash
# Clone the repository
git clone https://github.com/your-username/agentic-search.git
cd agentic-search

# Setup environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Configuration
Create a .env file based on the .env.example:

Bash
cp .env.example .env
# Edit .env to add your LangSmith API Key for tracing
Running the Agent
Bash
python -m src.main
📈 Observability & Evaluation
This project is built with Production-First observability. By integrating with LangSmith, every agentic decision—from tool selection to final synthesis—is traced and visualized.

Staff-Level Note: In a production setting, this architecture supports LLM-as-a-Judge evaluation. Each agent run can be automatically graded for "Faithfulness" (did it hallucinate?) and "Relevancy" (did it answer the user?), providing a data-driven path to model optimization.

🛡️ Guardrails & Safety
Iteration Limits: The graph is configured with a maximum recursion limit to prevent infinite tool-calling loops.

Context Truncation: Search results are pre-processed to ensure they fit within the 128k context window of the local model, preventing performance degradation.

Future Roadmap
[ ] Persistent Checkpointing: Add a SQLite backend to LangGraph to allow "resuming" interrupted agent sessions.

[ ] Multi-Agent Orchestration: Implementing a "Supervisor" pattern to delegate between specialized search and specialized code-execution agents.

[ ] Hybrid RAG: Integrating a local vector database (ChromaDB) to combine web search with internal documentation.