import { StateGraph, END, START } from '@langchain/langgraph';
import { HumanMessage, SystemMessage } from '@langchain/core/messages';
import { llm, validateApiKey } from '../src/utils/llm.js';
import { log, logSection, logError } from '../src/utils/logger.js';
import type { AgentState } from '../src/types/state.js';

async function technicalWorker(state: AgentState): Promise<Partial<AgentState>> {
  log('worker', 'Technical analysis running...');
  
  const messages = [
    new SystemMessage('You are a technical specialist. Focus on implementation, architecture, and tech details.'),
    new HumanMessage(`Task: ${state.task}`),
  ];

  const response = await llm.invoke(messages);
  
  return {
    workerResults: [...state.workerResults, {
      agent: 'technical-worker',
      type: 'technical',
      content: response.content as string,
      timestamp: new Date().toISOString(),
    }],
  };
}

async function businessWorker(state: AgentState): Promise<Partial<AgentState>> {
  log('worker', 'Business analysis running...');
  
  const messages = [
    new SystemMessage('You are a business analyst. Look at ROI, business impact, and strategic implications.'),
    new HumanMessage(`Task: ${state.task}`),
  ];

  const response = await llm.invoke(messages);
  
  return {
    workerResults: [...state.workerResults, {
      agent: 'business-worker',
      type: 'business',
      content: response.content as string,
      timestamp: new Date().toISOString(),
    }],
  };
}

async function consolidateWorkers(_state: AgentState): Promise<Partial<AgentState>> {
  log('system', 'Consolidating parallel results...');
  return { currentStep: 'manager' };
}

async function managerAgent(state: AgentState): Promise<Partial<AgentState>> {
  log('manager', 'Reviewing all worker results...');
  
  const allFindings = state.workerResults
    .map(r => `[${(r.type || 'worker').toUpperCase()}]\n${r.content || r.findings}`)
    .join('\n\n');
  
  const messages = [
    new SystemMessage('Review all findings and provide overall assessment.'),
    new HumanMessage(`Task: ${state.task}\n\nFindings:\n${allFindings}`),
  ];

  const response = await llm.invoke(messages);
  
  return {
    managerDecision: {
      approved: true,
      assessment: response.content as string,
      timestamp: new Date().toISOString(),
    },
    currentStep: 'conductor',
  };
}

async function conductorAgent(state: AgentState): Promise<Partial<AgentState>> {
  log('conductor', 'Final synthesis...');
  
  const allFindings = state.workerResults
    .map(r => `[${(r.type || 'worker').toUpperCase()}]\n${r.content || r.findings}`)
    .join('\n\n');
  
  const messages = [
    new SystemMessage('Create final comprehensive report from all analyses.'),
    new HumanMessage(`Task: ${state.task}\n\nFindings:\n${allFindings}\n\nManager: ${state.managerDecision?.assessment}`),
  ];

  const response = await llm.invoke(messages);
  
  return {
    finalOutput: response.content as string,
  };
}

function buildParallelGraph() {
  return new StateGraph<AgentState>({
    channels: {
      task: null,
      workerResults: null,
      managerDecision: null,
      finalOutput: null,
      currentStep: null,
    },
  })
    .addNode('technical', technicalWorker)
    .addNode('business', businessWorker)
    .addNode('consolidate', consolidateWorkers)
    .addNode('manager', managerAgent)
    .addNode('conductor', conductorAgent)
    .addEdge(START, 'technical')
    .addEdge('technical', 'business')
    .addEdge('business', 'consolidate')
    .addEdge('consolidate', 'manager')
    .addEdge('manager', 'conductor')
    .addEdge('conductor', END)
    .compile();
}

async function runParallel(): Promise<void> {
  try {
    validateApiKey();
    logSection('🚀 Parallel Workers Example');

    const app = buildParallelGraph();
    const task = 'Should our company migrate to microservices architecture?';
    
    console.log(`\n📋 Task: ${task}`);
    console.log('⚡ Running technical and business analysis sequentially...\n');
    
    const result = await app.invoke({
      task,
      workerResults: [],
      managerDecision: null,
      finalOutput: null,
      currentStep: 'workers',
    });

    logSection('📊 FINAL REPORT');
    console.log(result.finalOutput);
  } catch (error) {
    logError(error);
    process.exit(1);
  }
}

runParallel();
