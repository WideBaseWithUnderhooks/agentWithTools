import { HumanMessage, SystemMessage } from '@langchain/core/messages';
import { llm } from '../utils/llm.js';
import { log } from '../utils/logger.js';
import type { AgentState } from '../types/state.js';

export async function conductorAgent(state: AgentState): Promise<Partial<AgentState>> {
  log('conductor', 'Synthesizing final output...');

  const workerFindings = state.workerResults
    .map((r) => r.findings || r.content)
    .join('\n\n');
  
  const managerAssessment = state.managerDecision?.assessment || '';

  const messages = [
    new SystemMessage(
      'You are the conductor. Pull everything together from the workers and manager into something coherent and useful.'
    ),
    new HumanMessage(
      `Original Task: ${state.task}\n\nWorker Findings:\n${workerFindings}\n\nManager Assessment:\n${managerAssessment}\n\nGive me the final synthesis.`
    ),
  ];

  const response = await llm.invoke(messages);

  console.log('\n✅ Final output ready!');

  return {
    finalOutput: response.content as string,
    currentStep: 'end',
  };
}
