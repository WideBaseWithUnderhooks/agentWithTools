import { HumanMessage, SystemMessage } from '@langchain/core/messages';
import { llm } from '../utils/llm.js';
import { log } from '../utils/logger.js';
import type { AgentState, WorkerResult } from '../types/state.js';

export async function workerAgent(state: AgentState): Promise<Partial<AgentState>> {
  log('worker', 'Processing task...');
  
  const messages = [
    new SystemMessage(
      'You are a worker agent. Dig into the task and come back with solid findings. Be specific and practical.'
    ),
    new HumanMessage(`Task: ${state.task}`),
  ];

  const response = await llm.invoke(messages);
  
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
