import { buildGraph, createInitialState } from '../src/graph/builder.js';
import { validateApiKey } from '../src/utils/llm.js';
import { logSection, logError } from '../src/utils/logger.js';

async function runSimpleTask(): Promise<void> {
  try {
    validateApiKey();
    logSection('🚀 Simple Task Example');

    const app = buildGraph();
    const task = 'What are the top 3 programming languages for AI development in 2026?';

    console.log(`\n📋 Task: ${task}`);

    const initialState = createInitialState(task);
    const result = await app.invoke(initialState);

    logSection('📊 FINAL RESULTS');
    console.log('\n🎯 Final Output:');
    console.log(result.finalOutput);
  } catch (error) {
    logError(error);
    process.exit(1);
  }
}

runSimpleTask();
