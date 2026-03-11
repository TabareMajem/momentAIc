

export enum AgentType {
  SNIPER = 'SNIPER',
  GATEKEEPER = 'GATEKEEPER',
  CONTENT = 'CONTENT',
  MEDIA = 'MEDIA',
  WORKFLOW = 'WORKFLOW',
  GROWTH = 'GROWTH',
  RECRUITING = 'RECRUITING',
  LEGAL = 'LEGAL',
  SUPPORT = 'SUPPORT',
  PROCUREMENT = 'PROCUREMENT',
  MOBY = 'MOBY',
  MOBY_AUTONOMOUS = 'MOBY_AUTONOMOUS',
  LEMLIST_DOMINATION = 'LEMLIST_DOMINATION',
  VIRAL_GROWTH = 'VIRAL_GROWTH',
  GTM_EXEC = 'GTM_EXEC',
  GROWTH_MONITOR = 'GROWTH_MONITOR',
  DASHBOARD = 'DASHBOARD',
  HUB = 'HUB',
  CAMPAIGNS = 'CAMPAIGNS',
  ADMIN = 'ADMIN',
  SETTINGS = 'SETTINGS',
  CONTENT_CLAY = 'CONTENT_CLAY',
  VIRAL = 'VIRAL',
  MOBY_DTC = 'MOBY_DTC',
  COMPETITOR = 'COMPETITOR'
}

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  password?: string;
  role: 'USER' | 'EDITOR' | 'ADMIN';
  status: 'ACTIVE' | 'PENDING' | 'SUSPENDED';
  lastLogin: string;
  plan: 'STARTER' | 'PRO' | 'ENTERPRISE';

  // New Billing Fields
  apiMode?: 'PERSONAL' | 'PLATFORM';
  personalApiKey?: string;
  credits?: number;
}

export interface Lead {
  id: string;
  name: string;
  email: string;
  message: string;
  status: 'PENDING' | 'QUALIFIED' | 'TIRE_KICKER' | 'SPAM' | 'PARTNERSHIP';
  analysis?: {
    category: string;
    reasoning: string;
    suggestedReply: string;
  };
  timestamp: Date;
}

export interface SniperTarget {
  id: string;
  name: string;
  linkedinUrl: string;
  rawProfileText: string;
  icebreaker: string | null;
  status: 'NEW' | 'PROCESSED';
}

export interface ContentPiece {
  id: string;
  rawIdea: string;
  generatedAssets?: {
    linkedinPost: string;
    twitterThread: string[];
    blogOutline: string[];
    visualPrompt?: string;
    visualImage?: string;
  };
  createdAt: Date;
}

export interface ChartData {
  name: string;
  value: number;
}

export interface SystemStat {
  label: string;
  value: number;
  change: number;
  trend: 'UP' | 'DOWN' | 'NEUTRAL';
}

export interface N8nConfig {
  baseUrl: string;
  apiKey: string;
}

export interface N8nWorkflowData {
  name?: string;
  nodes: any[];
  connections: any;
  settings?: any;
}

// --- CLAY / GROWTH ENGINE TYPES ---

export type ColumnType = 'text' | 'url' | 'status' | 'enrichment';

export interface ClayColumn {
  id: string;
  label: string;
  type: ColumnType;
  width: number;
  enrichmentPrompt?: string;
}

export interface ClayRow {
  id: string;
  data: Record<string, any>;
}

export interface ClayTableData {
  columns: ClayColumn[];
  rows: ClayRow[];
}

// --- NEW AGENTS TYPES ---

export interface Candidate {
  id: string;
  name: string;
  role: string;
  resumeText: string;
  score?: number;
  analysis?: {
    summary: string;
    pros: string[];
    cons: string[];
    emailDraft: string;
  };
  status: 'NEW' | 'INTERVIEW' | 'REJECT' | 'HIRED';
}

export interface LegalRisk {
  clause: string;
  riskLevel: "HIGH" | "MEDIUM" | "LOW";
  explanation: string;
  suggestion: string;
}

export interface ContractAudit {
  id: string;
  filename: string;
  risks: LegalRisk[];
  timestamp: Date;
}

export interface Invoice {
  id: string;
  vendor: string;
  amount: number;
  date: string;
  items: string[];
  status: 'APPROVED' | 'FLAGGED' | 'PENDING';
  auditReason?: string;
}

// --- ADVANCED WORKFLOW TYPES (Yokaizen) ---

export interface WorkflowNode {
  id: string;
  type: string;
  name: string;
  config: any;
  position: { x: number; y: number };
  inputs: string[];
  outputs: string[];
}

export interface YokaizenWorkflow {
  id: string;
  name: string;
  description: string;
  version: string;
  category: string;
  nodes: WorkflowNode[];
  connections: any[];
  triggers: any[];
  settings: any;
  metadata: any;
}

// --- MOBY DTC AGENT TYPES ---

export interface MobyMetrics {
  revenue: number;
  spend: number;
  roas: number;
  aov: number;
  cac: number;
  conversionRate: number;
}

export interface MobyInsight {
  category: 'CREATIVE' | 'MEDIA' | 'RETENTION' | 'CRO' | 'INVENTORY';
  title: string;
  finding: string;
  recommendation: string;
  revenueImpact: number; // Estimated $ impact
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface MobyReport {
  generatedAt: Date;
  metrics: MobyMetrics;
  insights: MobyInsight[];
  totalOpportunity: number;
  strategySummary: string;
}

// --- BLEEDING EDGE TYPES ---

export interface QuantumState {
  dimension: string;
  status: 'COHERENT' | 'ENTANGLED' | 'SUPERPOSITION';
  probability: number;
  insight: string;
}

export interface IntegrationDiscovery {
  id: string;
  platform: string;
  type: 'API' | 'WEBHOOK' | 'HIDDEN_ENDPOINT';
  status: 'DISCOVERED' | 'CONNECTING' | 'INTEGRATED';
  potentialImpact: string;
}

export interface MarketNarrative {
  id: string;
  topic: string;
  currentSentiment: string;
  targetSentiment: string;
  strategy: string;
  tactics: string[];
}

export interface EcosystemNode {
  platform: string;
  status: 'COLONIZED' | 'INFILTRATING' | 'TARGETED';
  influenceScore: number; // 0-100
  action: string;
}

// --- VIRAL GROWTH ENGINE TYPES ---

export interface ViralPlatformStrategy {
  strategy: string;
  daily_actions: string[];
}

export interface ViralAutomationSequence {
  sequence_id: string;
  trigger_conditions: string;
  execution_steps: string[];
  success_criteria: string;
}

export interface ViralStrategyResult {
  campaign_overview: {
    product_analysis: string;
    target_metrics: {
      viral_coefficient: number;
      monthly_leads: number;
    };
    budget_allocation: string;
  };
  viral_strategy: {
    content_strategy: string;
    automation_blueprint: string;
    amplification_system: string;
  };
  platform_execution: {
    instagram?: ViralPlatformStrategy;
    tiktok?: ViralPlatformStrategy;
    linkedin?: ViralPlatformStrategy;
    youtube?: ViralPlatformStrategy;
    twitter?: ViralPlatformStrategy;
  };
  automation_sequences: ViralAutomationSequence[];
  shareToken?: string;
}