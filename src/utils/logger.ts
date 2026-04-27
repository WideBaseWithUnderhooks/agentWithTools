import { AgentType } from '../types/state.js';

const ICONS: Record<AgentType, string> = {
  worker: '🔧',
  manager: '👔',
  conductor: '🎭',
  system: '🚀',
};

export function log(agent: AgentType, message: string): void {
  const icon = ICONS[agent] || 'ℹ️';
  console.log(`\n${icon} ${agent.toUpperCase()}: ${message}`);
}

export function logSection(title: string): void {
  console.log('\n' + '='.repeat(60));
  console.log(title);
  console.log('='.repeat(60));
}

export function logError(error: unknown): void {
  console.error('\n❌ ERROR:', error instanceof Error ? error.message : String(error));
}
