
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import type { 
  AuthResponse, User, Startup, StartupCreate, SignalScores, 
  AgentChatRequest, AgentChatResponse, WeeklySprint, DailyStandup, 
  StandupStatus, EngagementMetrics, FinancialMetrics, InvestmentDashboardItem,
  ChatMessage, AdminStats, AgentInfo, Lead
} from '../types';
import { v4 as uuidv4 } from 'uuid';

// Fallback if environment variable isn't set
const API_URL = 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;
  private leadsStore: Lead[] = [
    { id: 'lead-1', startup_id: 'startup-1', company_name: 'CyberDyne Systems', contact_person: 'Miles Dyson', email: 'miles@cyberdyne.com', status: 'new', value: 50000, probability: 10, ai_notes: 'High value target. Focus on security protocols.' },
    { id: 'lead-2', startup_id: 'startup-1', company_name: 'Massive Dynamic', contact_person: 'Nina Sharp', email: 'nina@massive.com', status: 'outreach', value: 120000, probability: 30, last_interaction: new Date(Date.now() - 86400000).toISOString() },
    { id: 'lead-3', startup_id: 'startup-1', company_name: 'Wayne Enterprises', contact_person: 'Lucius Fox', email: 'l.fox@wayne.com', status: 'negotiation', value: 500000, probability: 75, last_interaction: new Date(Date.now() - 172800000).toISOString() },
    { id: 'lead-4', startup_id: 'startup-1', company_name: 'InGen', contact_person: 'John Hammond', email: 'j.hammond@ingen.com', status: 'closed_won', value: 1500000, probability: 100 }
  ];

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: { 'Content-Type': 'application/json' },
      timeout: 2000, 
    });

    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    this.client.interceptors.response.use(
      (res) => res,
      async (error) => {
        if (!error.response || error.code === 'ERR_NETWORK' || error.code === 'ECONNABORTED') {
          return this.handleMockRequest(error.config);
        }

        if (error.response?.status === 401) {
          this.logout();
          if (typeof window !== 'undefined' && !window.location.hash.includes('login') && !window.location.hash.includes('signup')) {
            window.location.href = '#/login';
          }
        }
        return Promise.reject(error);
      }
    );

    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token');
    }
  }

  setToken(token: string | null) {
    this.token = token;
    if (typeof window !== 'undefined') {
      token ? localStorage.setItem('access_token', token) : localStorage.removeItem('access_token');
    }
  }

  getToken() { return this.token; }
  logout() { this.setToken(null); }

  // === MOCK HANDLER ===
  private async handleMockRequest(config: AxiosRequestConfig): Promise<any> {
    const method = config.method?.toLowerCase();
    const url = config.url || '';
    
    await new Promise(resolve => setTimeout(resolve, 400));

    // Admin User Mock
    const mockUser: User = {
      id: 'user-1',
      email: 'founder@momentai.c',
      full_name: 'Neo Anderson',
      subscription_tier: 'god_mode',
      role: 'admin', // Auto-admin for demo
      onboarding_completed: true,
      created_at: new Date().toISOString(),
      status: 'active',
      credits: 999999
    };

    const mockAuthResponse: AuthResponse = {
      access_token: 'mock-jwt-token',
      refresh_token: 'mock-refresh-token',
      user_id: 'user-1',
      expires_at: Date.now() + 3600000
    };

    // AUTH
    if (url.includes('/auth/login') && method === 'post') {
      return { data: mockAuthResponse };
    }
    if (url.includes('/auth/signup') && method === 'post') {
      return { data: { message: 'User created', user_id: 'user-1' } };
    }
    if (url.includes('/auth/me')) {
      return { data: mockUser };
    }

    // BILLING / STRIPE MOCK
    if (url.includes('/billing/checkout') && method === 'post') {
        const { tier } = JSON.parse(config.data);
        await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate Stripe Processing
        // In real backend: return { url: 'https://checkout.stripe.com/...' }
        return { data: { success: true, message: `Stripe checkout for ${tier} initialized.` } };
    }

    // ADMIN
    if (url.includes('/admin/stats')) {
      const stats: AdminStats = {
        total_users: 1248,
        active_subscriptions: 890,
        total_revenue: 154000,
        agents_deployed: 4521
      };
      return { data: stats };
    }
    if (url.includes('/admin/users')) {
      const users: User[] = [
        mockUser,
        { ...mockUser, id: 'user-2', full_name: 'Sarah Connor', email: 'sarah@skynet.com', role: 'user', subscription_tier: 'starter', credits: 50 },
        { ...mockUser, id: 'user-3', full_name: 'John Wick', email: 'john@continental.com', role: 'user', subscription_tier: 'growth', credits: 500 },
      ];
      return { data: users };
    }

    // STARTUPS
    if (url.includes('/api/startups') && !url.includes('/api/startups/') && method === 'get') {
      const startups: Startup[] = [
        {
          id: 'startup-1',
          user_id: 'user-1',
          name: 'HyperScale AI',
          description: 'AI-driven logistics optimization for enterprise fleets.',
          stage: 'growth',
          industry: 'Logistics',
          team_size: 12,
          total_funding: 2500000,
          created_at: new Date(Date.now() - 86400000 * 90).toISOString(),
          updated_at: new Date().toISOString()
        }
      ];
      return { data: startups };
    }
    
    // Single Startup
    if (/\/api\/startups\/[\w-]+$/.test(url) && method === 'get' && !url.includes('/signals')) {
       return { data: {
          id: 'startup-1',
          user_id: 'user-1',
          name: 'HyperScale AI',
          description: 'AI-driven logistics optimization for enterprise fleets.',
          stage: 'growth',
          industry: 'Logistics',
          team_size: 12,
          total_funding: 2500000,
          created_at: new Date(Date.now() - 86400000 * 90).toISOString(),
          updated_at: new Date().toISOString()
       }};
    }

    // SIGNALS
    if (url.includes('/signals/history') && method === 'get') {
      const history: SignalScores[] = Array.from({ length: 30 }).map((_, i) => ({
        startup_id: 'startup-1',
        composite_score: 60 + Math.floor(Math.random() * 35),
        technical_velocity_score: 70 + Math.floor(Math.random() * 25),
        pmf_score: 60 + Math.floor(Math.random() * 30),
        capital_efficiency_score: 80 + Math.floor(Math.random() * 15),
        founder_performance_score: 75 + Math.floor(Math.random() * 20),
        calculated_at: new Date(Date.now() - (29 - i) * 86400000).toISOString()
      }));
      return { data: history };
    }

    if (url.includes('/signals') && method === 'get') {
      const scores: SignalScores = {
        startup_id: 'startup-1',
        composite_score: 88,
        technical_velocity_score: 92,
        pmf_score: 75,
        capital_efficiency_score: 95,
        founder_performance_score: 89,
        calculated_at: new Date().toISOString()
      };
      return { data: scores };
    }

    // SPRINTS
    if (url.includes('/sprints/current') && method === 'get') {
      const sprint: WeeklySprint = {
        id: 'sprint-101',
        startup_id: 'startup-1',
        week_start: new Date().toISOString(),
        weekly_goal: 'Ship the Quantum Engine v2',
        key_metric_name: 'API Latency',
        key_metric_start: 120,
        momentum_ai_feedback: 'Velocity is high. Ensure unit tests cover the new module.',
        created_at: new Date().toISOString()
      };
      return { data: sprint };
    }

    // AGENTS
    if (url.includes('/agents/available') && method === 'get') {
        return { 
            data: {
                available: [
                    { id: 'orchestrator', name: 'ORCHESTRATOR', description: 'Strategic command. The brain.', tier: 'starter', status: 'active' },
                    { id: 'technical_copilot', name: 'TECH-01', description: 'Systems Architect & Code Audit.', tier: 'starter', status: 'active' },
                    { id: 'business_copilot', name: 'BIZ-INTEL', description: 'Market domination strategies.', tier: 'growth', status: 'active' },
                    { id: 'sales_agent', name: 'HUNTER-V4', description: 'Outbound aggression.', tier: 'growth', status: 'active' }
                ],
                locked: [
                    { id: 'fundraising_copilot', name: 'VC-KILLER', description: 'Pitch perfection.', tier: 'god_mode', status: 'maintenance' },
                    { id: 'legal_agent', name: 'LEX-MACHINA', description: 'Ironclad contracts.', tier: 'god_mode', status: 'active' }
                ]
            }
        };
    }

    // CHAT
    if (url.includes('/agents/chat') && method === 'post') {
      const body = JSON.parse(config.data);
      const response: AgentChatResponse = {
        response: `[SYSTEM] Processing request: "${body.message}"...\n\nAnalysis complete. Based on current signal velocity (88/100), I recommend immediate deployment of the new feature set. Capital efficiency remains optimal.`,
        agent_used: body.agent_type,
        session_id: 'session-mock-1',
        tokens_used: 150,
        latency_ms: 120
      };
      return { data: response };
    }
    
    // INVESTMENT
    if (url.includes('/investment/dashboard')) {
        const item: InvestmentDashboardItem = {
            startup_id: 'startup-1',
            startup_name: 'HyperScale AI',
            stage: 'growth',
            composite_score: 88,
            technical_velocity_score: 92,
            pmf_score: 75,
            capital_efficiency_score: 95,
            founder_performance_score: 89,
            investment_status: 'Watching',
            investment_eligible: true,
            last_updated: new Date().toISOString()
        };
        return { data: [item] };
    }

    // LEADS (GROWTH ENGINE)
    if (url.includes('/growth/leads') && method === 'get') {
        // Return leads from mock store
        return { data: this.leadsStore };
    }
    if (url.includes('/growth/leads') && method === 'post') {
        const body = JSON.parse(config.data);
        const newLead = { ...body, id: uuidv4() };
        this.leadsStore.push(newLead);
        return { data: newLead };
    }
    if (url.includes('/growth/leads') && method === 'patch') {
        const body = JSON.parse(config.data);
        const id = url.split('/').pop();
        const index = this.leadsStore.findIndex(l => l.id === id);
        if (index !== -1) {
            this.leadsStore[index] = { ...this.leadsStore[index], ...body };
            return { data: this.leadsStore[index] };
        }
        return { data: {} };
    }

    // METRICS
    if (url.includes('/metrics')) return { data: { success: true } };

    return { data: { success: true } };
  }

  // === AUTH ===
  async signup(email: string, password: string, fullName: string) {
    const { data } = await this.client.post('/api/auth/signup', { email, password, full_name: fullName });
    return data;
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    const { data } = await this.client.post('/api/auth/login', { email, password });
    this.setToken(data.access_token);
    return data;
  }

  async getMe(): Promise<User> {
    const { data } = await this.client.get('/api/auth/me');
    return data;
  }

  // === BILLING ===
  async createCheckoutSession(tier: string): Promise<{ url?: string; success?: boolean }> {
    const { data } = await this.client.post('/api/billing/checkout', { tier });
    return data;
  }

  // === ADMIN ===
  async getAdminStats(): Promise<AdminStats> {
    const { data } = await this.client.get('/admin/stats');
    return data;
  }

  async getAdminUsers(): Promise<User[]> {
    const { data } = await this.client.get('/admin/users');
    return data;
  }

  // === STARTUPS ===
  async getStartups(): Promise<Startup[]> {
    const { data } = await this.client.get('/api/startups');
    return Array.isArray(data) ? data : [];
  }

  async getStartup(id: string): Promise<Startup> {
    const { data } = await this.client.get(`/api/startups/${id}`);
    return data;
  }

  async createStartup(payload: StartupCreate): Promise<Startup> {
    const { data } = await this.client.post('/api/startups', payload);
    return data;
  }

  async updateStartup(id: string, payload: Partial<StartupCreate>): Promise<Startup> {
    const { data } = await this.client.patch(`/api/startups/${id}`, payload);
    return data;
  }

  // === SIGNALS ===
  async getSignalScores(startupId: string): Promise<SignalScores> {
    const { data } = await this.client.get(`/api/startups/${startupId}/signals`);
    return data;
  }

  async getSignalHistory(startupId: string, days = 30): Promise<SignalScores[]> {
    const { data } = await this.client.get(`/api/startups/${startupId}/signals/history`, { params: { days } });
    return Array.isArray(data) ? data : [];
  }

  async recalculateSignals(startupId: string): Promise<SignalScores> {
    const { data } = await this.client.post(`/api/startups/${startupId}/signals/recalculate`);
    return data;
  }

  // === AGENTS ===
  async chatWithAgent(request: AgentChatRequest): Promise<AgentChatResponse> {
    const { data } = await this.client.post('/api/agents/chat', request);
    return data;
  }

  async getAvailableAgents() {
    const { data } = await this.client.get('/api/agents/available');
    return data;
  }

  async getAgentHistory(params?: { startup_id?: string; agent_type?: string; limit?: number }) {
    const { data } = await this.client.get('/api/agents/history', { params });
    return data;
  }

  // === MOMENTUM AI ===
  async createSprint(startupId: string, payload: { weekly_goal: string; key_metric_name?: string; key_metric_start?: number }): Promise<WeeklySprint> {
    const { data } = await this.client.post(`/api/startups/${startupId}/sprints`, payload);
    return data;
  }

  async getCurrentSprint(startupId: string): Promise<WeeklySprint | null> {
    const { data } = await this.client.get(`/api/startups/${startupId}/sprints/current`);
    return data.message ? null : data;
  }

  async submitSprintReview(startupId: string, sprintId: string, payload: { goal_achieved: boolean; learnings: string; key_metric_end?: number }): Promise<WeeklySprint> {
    const { data } = await this.client.post(`/api/startups/${startupId}/sprints/${sprintId}/review`, payload);
    return data;
  }

  async submitMorningStandup(startupId: string, goal: string): Promise<DailyStandup> {
    const { data } = await this.client.post(`/api/startups/${startupId}/standups/morning`, { morning_goal: goal });
    return data;
  }

  async submitEveningStandup(startupId: string, payload: { evening_result: string; proof_url?: string; goal_completed: boolean }): Promise<DailyStandup> {
    const { data } = await this.client.post(`/api/startups/${startupId}/standups/evening`, payload);
    return data;
  }

  async getTodayStandup(startupId: string): Promise<StandupStatus> {
    const { data } = await this.client.get(`/api/startups/${startupId}/standups/today`);
    return data;
  }

  // === GROWTH ENGINE ===
  async getLeads(startupId: string): Promise<Lead[]> {
    const { data } = await this.client.get(`/api/growth/leads?startupId=${startupId}`);
    return data;
  }

  async updateLead(id: string, updates: Partial<Lead>): Promise<Lead> {
    const { data } = await this.client.patch(`/api/growth/leads/${id}`, updates);
    return data;
  }

  async createLead(lead: Partial<Lead>): Promise<Lead> {
    const { data } = await this.client.post('/api/growth/leads', lead);
    return data;
  }

  // === METRICS ===
  async submitEngagementMetrics(startupId: string, payload: EngagementMetrics) {
    await this.client.post(`/api/startups/${startupId}/metrics/engagement`, payload);
  }

  async submitFinancialMetrics(startupId: string, payload: FinancialMetrics) {
    await this.client.post(`/api/startups/${startupId}/metrics/financial`, payload);
  }

  // === INVESTMENT ===
  async getInvestmentDashboard(): Promise<InvestmentDashboardItem[]> {
    const { data } = await this.client.get('/api/investment/dashboard');
    return Array.isArray(data) ? data : [];
  }
}

export const api = new ApiClient();
