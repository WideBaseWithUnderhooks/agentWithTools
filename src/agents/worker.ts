import { HumanMessage, SystemMessage } from '@langchain/core/messages';
import { workerLLM } from '../utils/llm.js';
import { log } from '../utils/logger.js';
import type { AgentState, WorkerResult } from '../types/state.js';

export async function workerAgent(state: AgentState): Promise<Partial<AgentState>> {
  const iteration = (state.iterations || 0) + 1;
  log('worker', `Processing task... (Iteration ${iteration})`);

  const isRevision = (state.iterations || 0) > 0;
  const previousFeedback = state.managerDecision?.feedback || '';

  const systemPrompt = isRevision
    ? `You are a worker agent. The manager reviewed your previous work and requested revisions.

Previous feedback: ${previousFeedback}

Address the feedback and improve your analysis. Be specific and practical.`
    : 'You are a worker agent. Dig into the task and come back with solid findings. Be specific and practical.';

  const messages = [
    new SystemMessage(systemPrompt),
    new HumanMessage(`Task: ${state.task}`),
  ];

  if (isRevision && state.workerResults.length > 0) {
    const previousWork = state.workerResults[state.workerResults.length - 1].findings;
    messages.push(
      new HumanMessage(`Your previous analysis:\n${previousWork}\n\nImprove based on the feedback above.`)
    );
  }

  const response = await workerLLM.invoke(messages);

  const result: WorkerResult = {
    agent: 'worker',
    findings: response.content as string,
    timestamp: new Date().toISOString(),
  };

  const preview = result.findings?.substring(0, 100) || '';
  console.log(`Worker findings: ${preview}...`);

  return {
    workerResults: [...state.workerResults, result],
    currentStep: 'manager',
  };
}
