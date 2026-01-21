
// User & Auth
export type SubscriptionTier = 'starter' | 'growth' | 'god_mode';

export interface User {
  id: string;
  email: string;
  full_name: string;
  subscription_tier: SubscriptionTier;
  role: 'user' | 'admin';
  onboarding_completed: boolean;
  avatar_url?: string;
  created_at: string;
  status: 'active' | 'banned';
  credits: number; // New: Currency for AI actions
  is_superuser?: boolean;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user_id: string;
  expires_at: number;
}

// Admin
export interface HunterStats {
  leads_generated: number;
  emails_sent: number;
  campaigns_active: number;
}

export interface AdminStats {
  total_users: number;
  active_subscriptions: number;
  total_revenue: number;
  agents_deployed: number;
  hunter_stats: HunterStats;
}

// Startup
export type StartupStage = 'idea' | 'mvp' | 'growth' | 'scale';

export interface Startup {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  website?: string;
  github_url?: string;
  stage: StartupStage;
  industry?: string;
  team_size: number;
  total_funding: number;
  logo_url?: string;
  created_at: string;
  updated_at: string;
}

export interface StartupCreate {
  name: string;
  description?: string;
  website?: string;
  github_url?: string;
  stage: StartupStage;
  industry?: string;
}

// Signal Scores
export interface SignalScores {
  startup_id: string;
  technical_velocity_score: number;
  pmf_score: number;
  capital_efficiency_score: number;
  founder_performance_score: number;
  composite_score: number;
  calculated_at: string;
}

// Agents
export type AgentType =
  | 'orchestrator' | 'technical_copilot' | 'business_copilot'
  | 'fundraising_coach' | 'momentum_ai' | 'sales_agent'
  | 'content_agent' | 'legal_agent' | 'data_agent'
  | 'elon_musk' | 'paul_graham'
  | 'onboarding_coach' | 'competitor_intel';

export interface AgentInfo {
  id: AgentType;
  name: string;
  description: string;
  tier: SubscriptionTier;
  status: 'active' | 'maintenance' | 'deprecated';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  agent_used?: AgentType;
  timestamp: Date;
  isStreaming?: boolean;
}

export interface AgentChatRequest {
  message: string;
  agent_type: AgentType;
  startup_id?: string;
  session_id?: string;
  conversation_history?: Array<{ role: string; content: string }>;
}

export interface AgentChatResponse {
  response: string;
  agent_used: AgentType;
  session_id: string;
  tokens_used: number;
  latency_ms: number;
}

// Momentum AI
export interface WeeklySprint {
  id: string;
  startup_id: string;
  week_start: string;
  weekly_goal: string;
  key_metric_name?: string;
  key_metric_start?: number;
  key_metric_end?: number;
  goal_achieved?: boolean;
  learnings?: string;
  momentum_ai_feedback?: string;
  created_at: string;
}

export interface DailyStandup {
  id: string;
  standup_date: string;
  morning_goal?: string;
  morning_submitted_at?: string;
  evening_result?: string;
  evening_submitted_at?: string;
  goal_completed?: boolean;
  momentum_ai_response?: string;
}

export interface StandupStatus {
  date: string;
  morning_submitted: boolean;
  evening_submitted: boolean;
  data?: DailyStandup;
}

// Investment
export interface InvestmentDashboardItem {
  startup_id: string;
  startup_name: string;
  stage: StartupStage;
  composite_score: number;
  technical_velocity_score: number;
  pmf_score: number;
  capital_efficiency_score: number;
  founder_performance_score: number;
  investment_status: string;
  investment_eligible: boolean;
  last_updated?: string;
}

// Metrics
export interface EngagementMetrics {
  dau?: number;
  wau?: number;
  mau?: number;
  retention_d1?: number;
  retention_d7?: number;
  retention_d30?: number;
  nps_score?: number;
  churn_rate?: number;
}

export interface FinancialMetrics {
  mrr?: number;
  burn_rate?: number;
  runway_months?: number;
  ltv?: number;
  cac?: number;
}

// --- AGENT FORGE ---

export type NodeType = 'webhook' | 'supervisor' | 'browser' | 'mcp' | 'human' | 'end' | 'start';

export interface WorkflowNode {
  id: string;
  type: NodeType;
  position: { x: number; y: number };
  data: {
    label: string;
    description?: string;
    status: 'idle' | 'running' | 'completed' | 'failed' | 'waiting';
    systemInstruction?: string;
    tools?: string[];
    config?: Record<string, any>;
  };
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  animated?: boolean;
}

export interface WorkflowLog {
  id: string;
  timestamp: string;
  level: 'info' | 'success' | 'warning' | 'error' | 'system';
  message: string;
  nodeId?: string;
}

export interface ApprovalRequest {
  id: string;
  workflowId: string;
  nodeId: string;
  title: string;
  payload: any;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
}

// --- GROWTH ENGINE ---

export type LeadStatus = 'new' | 'outreach' | 'negotiation' | 'closed_won' | 'closed_lost';

export interface Lead {
  id: string;
  startup_id: string;
  company_name: string;
  contact_person: string;
  email: string;
  status: LeadStatus;
  value: number;
  last_interaction?: string;
  ai_notes?: string;
  probability: number;
}

// --- AMBASSADOR & REFERRAL ---
export interface AmbassadorProfileResponse {
  is_ambassador: boolean;
  profile?: {
    id: string;
    user_id: string;
    referral_code: string;
    total_earnings: number;
    unpaid_earnings: number;
    status: 'pending' | 'approved' | 'rejected';
  };
  stripe_connected: boolean;
}

export interface ReferralStatsResponse {
  total_referrals: number;
  active_referrals: number;
  total_earnings: number;
  referral_code: string;
  links: string[];
}

// --- GROWTH ANALYTICS (Phase 12) ---
export interface EmpireStatus {
  current_step: number;
  step_data: Record<string, any>;
  completed_at?: string;
}
