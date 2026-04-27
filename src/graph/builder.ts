import { StateGraph, START } from '@langchain/langgraph';
import { workerAgent } from '../agents/worker.js';
import { managerAgent } from '../agents/manager.js';
import { conductorAgent } from '../agents/conductor.js';
import { routeAfterWorker, routeAfterManager, routeAfterConductor } from './router.js';
import type { AgentState } from '../types/state.js';

export function buildGraph() {
  return new StateGraph<AgentState>({
    channels: {
      task: null,
      workerResults: null,
      managerDecision: null,
      finalOutput: null,
      currentStep: null,
      iterations: null,
    },
  })
    .addNode('worker', workerAgent)
    .addNode('manager', managerAgent)
    .addNode('conductor', conductorAgent)
    .addEdge(START, 'worker')
    .addConditionalEdges('worker', routeAfterWorker)
    .addConditionalEdges('manager', routeAfterManager)
    .addConditionalEdges('conductor', routeAfterConductor)
    .compile();
}

export function createInitialState(task: string): AgentState {
  return {
    task,
    workerResults: [],
    managerDecision: null,
    finalOutput: null,
    currentStep: 'worker',
    iterations: 0,
  };
}
