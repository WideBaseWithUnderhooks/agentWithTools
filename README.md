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

Set up your API key in `.env`:
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

## Building Your Own Agent

Want to add a custom agent? Just create a new function that takes the state and returns an updated state:

```typescript
async function myAgent(state: AgentState): Promise<Partial<AgentState>> {
  // do your thing
  return { /* your partial state changes */ };
}
```

Then wire it into the graph in `src/graph/builder.ts`.

## Why I Built This

I wanted to see how well LangGraph handles multi-agent orchestration. The worker-manager-conductor pattern seemed like a good way to split up complex tasks, and it turns out it works pretty well.

## Notes

- Uses GPT-4 by default (you can change this in `src/utils/llm.ts`)
- TypeScript gives you nice type safety
- The graph structure makes it easy to add more agents or change the flow

Feel free to fork this and mess around with it. Pull requests welcome if you build something cool.

## License

MIT
