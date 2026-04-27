# WIP
# Multi-Agent Conductor System

A TypeScript multi-agent AI system built with LangGraph. I put this together to experiment with the worker-manager-conductor pattern for orchestrating AI agents.

## What It Does

The system has three types of agents working together:

- **Workers** - These guys do the actual work. They dig into tasks and come back with findings.
- **Managers** - They review what the workers found and decide if it's good enough or needs more work.
- **Conductors** - They pull everything together and produce the final output.

## The Flow

```
Worker does the analysis
    ↓
Manager reviews it
    ↓
Conductor synthesizes everything
    ↓
You get your result
```

## Getting Started

Install dependencies:
```bash
npm install
```

Set up your API key in local `.env`:
```
OPENAI_API_KEY=your_key_here
```

Run it:
```bash
npm run dev
```

## Examples

I included a few examples to show different ways you can use this:

**Simple task** (one worker → manager → conductor):
```bash
npm run example:simple
```

**Advanced** (multiple specialized workers):
```bash
npm run example:advanced
```

**Parallel execution** (workers running at the same time):
```bash
npm run example:parallel
```

## Project Structure

```
src/
├── types/          - TypeScript interfaces
├── agents/         - Worker, manager, and conductor implementations
├── graph/          - LangGraph workflow setup
└── utils/          - Helper functions

examples/           - Different usage patterns
```

## Building Agents:

Just create a new function that takes the state and returns an updated state:

```typescript
async function myAgent(state: AgentState): Promise<Partial<AgentState>> {
  // do your thing
  return { /* your partial state changes */ };
}
```

Then wire it into the graph in `src/graph/builder.ts`.


## Notes

- WIP to use GPT-4 by default (you can change this in `src/utils/llm.ts`)
- initial shell for AI news/blog(s) and aggregator
- developed with using ollama locally
- The graph structure makes it easy to add more agents or change the flow

