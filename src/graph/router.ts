import { END } from '@langchain/langgraph';
import type { AgentState, RouteDecision } from '../types/state.js';

export function routeAgent(state: AgentState): RouteDecision {
  if (state.currentStep === 'manager') {
    return 'manager';
  } else if (state.currentStep === 'conductor') {
    return 'conductor';
  } else if (state.currentStep === 'end') {
    return END;
  }
  return 'worker';
}
