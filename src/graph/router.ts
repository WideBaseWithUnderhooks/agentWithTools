import { END } from '@langchain/langgraph';
import type { AgentState, RouteDecision } from '../types/state.js';

const MAX_ITERATIONS = 3;

export function routeAfterWorker(_state: AgentState): RouteDecision {
  return 'manager';
}

export function routeAfterManager(state: AgentState): RouteDecision {
  if ((state.iterations || 0) >= MAX_ITERATIONS) {
    console.warn('⚠️  Max iterations reached, forcing completion');
    return 'conductor';
  }

  if (state.managerDecision?.approved) {
    return 'conductor';
  }

  return 'worker';
}

export function routeAfterConductor(_state: AgentState): RouteDecision {
  return END;
}
