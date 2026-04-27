import { StateGraph, END, START } from '@langchain/langgraph';
import { HumanMessage, SystemMessage } from '@langchain/core/messages';
import { llm, validateApiKey } from '../src/utils/llm.js';
import { log, logSection, logError } from '../src/utils/logger.js';
import type { AgentState, WorkerResult, ManagerDecision } from '../src/types/state.js';

async function researchWorker(state: AgentState): Promise<Partial<AgentState>> {
  log('worker', 'Gathering research data...');
  
  const messages = [
    new SystemMessage('You are a research specialist. Dig up comprehensive information on the topic.'),
    new HumanMessage(`Research topic: ${state.task}`),
  ];

  const response = await llm.invoke(messages);
  
  const result: WorkerResult = {
    agent: 'research-worker',
    type: 'research',
    content: response.content as string,
    timestamp: new Date().toISOString(),
  };
  
  return {
    workerResults: [...state.workerResults, result],
  };
}

async function analysisWorker(state: AgentState): Promise<Partial<AgentState>> {
  log('worker', 'Running analysis...');
  
  const researchData = state.workerResults.find(r => r.type === 'research')?.content || '';
  
  const messages = [
    new SystemMessage('You are an analyst. Take the research and find the patterns and insights.'),
    new HumanMessage(`Research data:\n${researchData}\n\nWhat does this tell us?`),
  ];

  const response = await llm.invoke(messages);
  
  const result: WorkerResult = {
    agent: 'analysis-worker',
    type: 'analysis',
    content: response.content as string,
    timestamp: new Date().toISOString(),
  };
  
  return {
    workerResults: [...state.workerResults, result],
  };
}

async function managerAgent(state: AgentState): Promise<Partial<AgentState>> {
  log('manager', 'Reviewing everything...');
  
  const allFindings = state.workerResults
    .map(r => `[${(r.type || 'worker').toUpperCase()}]\n${r.content || r.findings}`)
    .join('\n\n');
  
  const messages = [
    new SystemMessage('You are a manager. Look over all the work and decide if we are good to move forward or if something needs another pass.'),
    new HumanMessage(`Task: ${state.task}\n\nWorker Outputs:\n${allFindings}\n\nShould we proceed? Reply with APPROVED or REVISION_NEEDED.`),
  ];

  const response = await llm.invoke(messages);
  const approved = (response.content as string).toUpperCase().includes('APPROVED');
  
  const decision: ManagerDecision = {
    approved,
    feedback: response.content as string,
    assessment: response.content as string,
    timestamp: new Date().toISOString(),
  };
  
  return {
    managerDecision: decision,
    iterations: (state.iterations || 0) + 1,
  };
}

async function conductorAgent(state: AgentState): Promise<Partial<AgentState>> {
  log('conductor', 'Putting it all together...');
  
  const allFindings = state.workerResults
    .map(r => `[${(r.type || 'worker').toUpperCase()}]\n${r.content || r.findings}`)
    .join('\n\n');
  
  const messages = [
    new SystemMessage('You are the conductor. Build a solid final report from everything.'),
    new HumanMessage(`Task: ${state.task}\n\nAll Findings:\n${allFindings}\n\nManager Feedback:\n${state.managerDecision?.feedback}\n\nCreate final report.`),
  ];

  const response = await llm.invoke(messages);
  
  return {
    finalOutput: response.content as string,
  };
}

function routeNext(state: AgentState): string {
  if ((state.iterations || 0) > 2) {
    return 'conductor';
  }
  
  if (!state.workerResults.find(r => r.type === 'research')) {
    return 'research';
  }
  
  if (!state.workerResults.find(r => r.type === 'analysis')) {
    return 'analysis';
  }
  
  if (!state.managerDecision) {
    return 'manager';
  }
  
  return 'conductor';
}

function buildAdvancedGraph() {
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
    .addNode('research', researchWorker)
    .addNode('analysis', analysisWorker)
    .addNode('manager', managerAgent)
    .addNode('conductor', conductorAgent)
    .addEdge(START, 'research')
    .addConditionalEdges('research', routeNext)
    .addConditionalEdges('analysis', routeNext)
    .addConditionalEdges('manager', routeNext)
    .addEdge('conductor', END)
    .compile();
}

async function runAdvanced(): Promise<void> {
  try {
    validateApiKey();
    logSection('🚀 Advanced Multi-Worker Example');

    const app = buildAdvancedGraph();
    
    const task = 'What are the emerging trends in AI safety and alignment research for 2026?';
    console.log(`\n📋 Task: ${task}`);
    
    const result = await app.invoke({
      task,
      workerResults: [],
      managerDecision: null,
      finalOutput: null,
      currentStep: 'research',
      iterations: 0,
    });

    logSection('📊 FINAL REPORT');
    console.log(result.finalOutput);
  } catch (error) {
    logError(error);
    process.exit(1);
  }
}

runAdvanced();
