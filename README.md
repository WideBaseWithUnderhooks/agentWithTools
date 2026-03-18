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








lkajsdlkfjal;skdjf

laksjdflkj

agentWithTools
Agent With Tools — Local Agentic Search using the ReAct Pattern

A high-performance, local-first search agent built with LangGraph and Ollama. This project implements the ReAct pattern (Reasoning plus Acting) so an LLM can autonomously navigate web search and tool calls to answer complex, real-time queries.

Key Features
State Machine architecture for non-deterministic agent flows

Cyclic graph reflection to refine queries when tool outputs are insufficient

Decoupled tool registry so tools are modular plugins under src/tools/

Local-first inference using Ollama Llama 3.2 for zero data egress and low latency

Production-grade observability via LangSmith tracing

Architecture and Design Decisions
State Management LangGraph
Cyclic Graphs  
Allows the agent to loop back and re-evaluate tool outputs, enabling iterative refinement rather than a single linear pass.

Reducer Patterns  
Uses add_messages style reducers to manage conversation state and memory buffers without manual list manipulation.

Decoupled Tool Registry
Separation of Concerns  
Tools live in src/tools/ as modular plugins. Adding capabilities like SQL execution or File I/O does not require changing core orchestration.

Schema Introspection  
Uses LangChain style @tool decorators to auto-generate JSON schemas and enforce strict contracts between the LLM and execution environment.

Local First Inference
Ollama Integration  
Optimized for Llama 3.2 3b to leverage native tool-calling fine-tuning. This provides advanced orchestration logic with no external data egress and minimal latency.

Tech Stack
Orchestration: LangGraph
LLM Provider: Ollama Llama 3.2 3b
Search Engine: DuckDuckGo via langchain-community
Environment: Python 3.11 or newer
Observability: LangSmith with OpenTelemetry compatible tracing

Getting Started
Prerequisites
Ollama installed. See Ollama documentation for installation steps.

Python 3.11+

Pull the Model
bash
ollama pull llama3.2:3b
Installation
bash
# Clone the repository
git clone https://github.com/your-username/agentic-search.git
cd agentic-search

# Setup environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Configuration
bash
# Create a .env file from the example
cp .env.example .env
# Edit .env to add your LangSmith API key for tracing
Run the Agent
bash
python -m src.main
Observability and Evaluation
Production First Tracing  
Every agent decision is traced with LangSmith so tool selection, intermediate reasoning, and final synthesis are visible.

LLM as a Judge  
The architecture supports automated grading of runs for Faithfulness and Relevancy, enabling data-driven model optimization.

Guardrails and Safety
Iteration Limits  
The graph enforces a maximum recursion depth to prevent infinite tool-calling loops.

Context Truncation  
Search results are pre-processed and truncated to fit within the model context window to avoid performance degradation.

Project Roadmap
[ ] Persistent Checkpointing Add a SQLite backend to LangGraph to resume interrupted sessions

[ ] Multi-Agent Orchestration Implement a Supervisor pattern to delegate between specialized agents

[ ] Hybrid RAG Integrate a local vector database such as ChromaDB to combine web search with internal docs