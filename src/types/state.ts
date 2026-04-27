export interface WorkerResult {
  agent: string;
  type?: string;
  findings?: string;
  content?: string;
  timestamp: string;
}

export interface ManagerDecision {
  assessment: string;
  approved: boolean;
  timestamp: string;
  feedback?: string;
}

export interface AgentState {
  task: string;
  workerResults: WorkerResult[];
  managerDecision: ManagerDecision | null;
  finalOutput: string | null;
  currentStep: string;
  iterations?: number;
}

export type AgentType = 'worker' | 'manager' | 'conductor' | 'system';

export type RouteDecision = 'worker' | 'manager' | 'conductor' | '__end__';
