import { HumanMessage, SystemMessage } from '@langchain/core/messages';
import { llm } from '../utils/llm.js';
import { log } from '../utils/logger.js';
import type { AgentState, ManagerDecision } from '../types/state.js';

export async function managerAgent(state: AgentState): Promise<Partial<AgentState>> {
  log('manager', 'Reviewing worker results...');

  const workerFindings = state.workerResults
    .map((r) => r.findings || r.content)
    .join('\n\n');

  const messages = [
    new SystemMessage(
      'You are a manager agent. Review what the workers found and decide if it holds up. Check for quality and completeness.'
    ),
    new HumanMessage(
      `Original Task: ${state.task}\n\nWorker Findings:\n${workerFindings}\n\nWhat's your take on this?`
    ),
  ];

  const response = await llm.invoke(messages);
  
  const decision: ManagerDecision = {
    assessment: response.content as string,
    approved: true,
    timestamp: new Date().toISOString(),
  };

  const preview = decision.assessment.substring(0, 100);
  console.log(`Manager decision: ${preview}...`);

  return {
    managerDecision: decision,
    currentStep: 'conductor',
  };
}
