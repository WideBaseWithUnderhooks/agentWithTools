import { ChatOpenAI } from '@langchain/openai';
import dotenv from 'dotenv';

dotenv.config();

export const workerLLM = new ChatOpenAI({
  modelName: 'gpt-4o',
  temperature: 0.7,
  openAIApiKey: process.env.OPENAI_API_KEY,
});

export const managerLLM = new ChatOpenAI({
  modelName: 'gpt-4o',
  temperature: 0.3,
  openAIApiKey: process.env.OPENAI_API_KEY,
});

export const conductorLLM = new ChatOpenAI({
  modelName: 'gpt-4o',
  temperature: 0.5,
  openAIApiKey: process.env.OPENAI_API_KEY,
});

// Default LLM for backward compatibility with existing examples
export const llm = workerLLM;

export function validateApiKey(): void {
  if (!process.env.OPENAI_API_KEY) {
    throw new Error('OPENAI_API_KEY is not set in environment variables');
  }
}
