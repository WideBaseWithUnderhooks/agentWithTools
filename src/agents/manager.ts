import { HumanMessage, SystemMessage } from '@langchain/core/messages';
import { managerLLM } from '../utils/llm.js';
import { log } from '../utils/logger.js';
import type { AgentState, ManagerDecision } from '../types/state.js';

export async function managerAgent(state: AgentState): Promise<Partial<AgentState>> {
  log('manager', 'Reviewing worker results...');

  const workerFindings = state.workerResults
    .map((r) => r.findings || r.content)
    .join('\n\n');

  const messages = [
    new SystemMessage(
      `You are a manager agent. Review the worker's findings critically.

Assess:
- Completeness: Does it fully address the task?
- Quality: Is the analysis thorough and well-reasoned?
- Accuracy: Are there any obvious gaps or errors?

Respond with:
APPROVED - if the work is good enough
NEEDS_REVISION - if it needs more work

Then provide your assessment and any feedback.`
    ),
    new HumanMessage(
      `Original Task: ${state.task}\n\nWorker Findings:\n${workerFindings}\n\nWhat's your decision?`
    ),
  ];

  const response = await managerLLM.invoke(messages);
  const content = response.content as string;
  const approved =
    content.toUpperCase().includes('APPROVED') &&
    !content.toUpperCase().includes('NEEDS_REVISION');

  const decision: ManagerDecision = {
    assessment: content,
    approved,
    timestamp: new Date().toISOString(),
    feedback: approved ? undefined : content,
  };

  console.log(`Manager decision: ${approved ? '✅ APPROVED' : '❌ NEEDS REVISION'}`);

  return {
    managerDecision: decision,
    currentStep: approved ? 'conductor' : 'worker',
    iterations: (state.iterations || 0) + 1,
  };
}
