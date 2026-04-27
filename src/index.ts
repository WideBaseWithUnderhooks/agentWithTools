import { buildGraph, createInitialState } from './graph/builder.js';
import { validateApiKey } from './utils/llm.js';
import { logSection, logError } from './utils/logger.js';

async function main(): Promise<void> {
  try {
    validateApiKey();

    logSection('🚀 Multi-Agent System Starting Up');

    const app = buildGraph();

    const task = 'Analyze the potential benefits and risks of implementing a 4-day work week in a tech company with 200 employees.';

    console.log(`\n📋 Task: ${task}`);
    logSection('Processing...');

    const initialState = createInitialState(task);
    const result = await app.invoke(initialState);

    logSection('📊 FINAL RESULTS');
    console.log('\n🎯 Final Output:');
    console.log(result.finalOutput);
    console.log('\n' + '='.repeat(60));
  } catch (error) {
    logError(error);
    process.exit(1);
  }
}

main();
