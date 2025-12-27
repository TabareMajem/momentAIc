
import axios, { AxiosInstance } from 'axios';
import type {
  AuthResponse, User, Startup, StartupCreate, SignalScores,
  AgentChatRequest, AgentChatResponse, WeeklySprint, DailyStandup,
  StandupStatus, EngagementMetrics, FinancialMetrics, InvestmentDashboardItem,
  ChatMessage, AdminStats, AgentInfo, Lead, AmbassadorProfileResponse, ReferralStatsResponse
} from '../types';

// Production: empty string means same-origin (relative /api/ calls via Nginx proxy)
// Development: localhost:8000 for local backend
const API_URL = import.meta.env.VITE_API_URL !== undefined
  ? import.meta.env.VITE_API_URL
  : ''; // Default to relative path for production (proxied via Nginx)

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: { 'Content-Type': 'application/json' },
      timeout: 30000, // 30 seconds for production
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

  // === AUTH ===
  async signup(email: string, password: string, fullName: string) {
    const { data } = await this.client.post('/api/v1/auth/signup', { email, password, full_name: fullName });
    return data;
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    const { data } = await this.client.post('/api/v1/auth/login', { email, password });
    // Backend returns { user, tokens: { access_token, refresh_token } }
    const token = data.tokens?.access_token || data.access_token;
    this.setToken(token);
    return data;
  }


  async getMe(): Promise<User> {
    const { data } = await this.client.get('/api/v1/auth/me');
    // Map backend field names to frontend expected names
    return {
      ...data,
      subscription_tier: data.tier || data.subscription_tier || 'starter',
      credits: data.credits_balance ?? data.credits ?? 0,
    };
  }


  // === BILLING ===
  async createCheckoutSession(tier: string): Promise<{ url?: string; success?: boolean }> {
    const { data } = await this.client.post('/api/v1/billing/checkout', { tier });
    return data;
  }

  // === ADMIN ===
  async getAdminStats(): Promise<AdminStats> {
    const { data } = await this.client.get('/api/v1/admin/stats');
    return data;
  }

  async getAdminUsers(): Promise<User[]> {
    const { data } = await this.client.get('/api/v1/admin/users');
    return data;
  }

  // === STARTUPS ===
  async getStartups(): Promise<Startup[]> {
    const { data } = await this.client.get('/api/v1/startups');
    return Array.isArray(data) ? data : [];
  }

  async getStartup(id: string): Promise<Startup> {
    const { data } = await this.client.get(`/api/v1/startups/${id}`);
    return data;
  }

  async createStartup(payload: StartupCreate): Promise<Startup> {
    const { data } = await this.client.post('/api/v1/startups', payload);
    return data;
  }

  async updateStartup(id: string, payload: Partial<StartupCreate>): Promise<Startup> {
    const { data } = await this.client.patch(`/api/v1/startups/${id}`, payload);
    return data;
  }

  // === SIGNALS ===
  async getSignalScores(startupId: string): Promise<SignalScores> {
    const { data } = await this.client.get(`/api/v1/startups/${startupId}/signals`);
    return data;
  }

  async getSignalHistory(startupId: string, days = 30): Promise<SignalScores[]> {
    const { data } = await this.client.get(`/api/v1/startups/${startupId}/signals/history`, { params: { days } });
    return Array.isArray(data) ? data : [];
  }

  async recalculateSignals(startupId: string): Promise<SignalScores> {
    const { data } = await this.client.post(`/api/v1/startups/${startupId}/signals/recalculate`);
    return data;
  }

  // === AGENTS ===
  async chatWithAgent(request: AgentChatRequest): Promise<AgentChatResponse> {
    const { data } = await this.client.post('/api/v1/agents/chat', request);
    return data;
  }

  async getAvailableAgents() {
    const { data } = await this.client.get('/api/v1/agents/available');
    return data;
  }

  async getAgentHistory(params?: { startup_id?: string; agent_type?: string; limit?: number }) {
    const { data } = await this.client.get('/api/v1/agents/history', { params });
    return data;
  }

  // === MOMENTUM AI ===
  async createSprint(startupId: string, payload: { weekly_goal: string; key_metric_name?: string; key_metric_start?: number }): Promise<WeeklySprint> {
    const { data } = await this.client.post(`/api/v1/startups/${startupId}/sprints`, payload);
    return data;
  }

  async getCurrentSprint(startupId: string): Promise<WeeklySprint | null> {
    const { data } = await this.client.get(`/api/v1/startups/${startupId}/sprints/current`);
    return data.message ? null : data;
  }

  async submitSprintReview(startupId: string, sprintId: string, payload: { goal_achieved: boolean; learnings: string; key_metric_end?: number }): Promise<WeeklySprint> {
    const { data } = await this.client.post(`/api/v1/startups/${startupId}/sprints/${sprintId}/review`, payload);
    return data;
  }

  async submitMorningStandup(startupId: string, goal: string): Promise<DailyStandup> {
    const { data } = await this.client.post(`/api/v1/startups/${startupId}/standups/morning`, { morning_goal: goal });
    return data;
  }

  async submitEveningStandup(startupId: string, payload: { evening_result: string; proof_url?: string; goal_completed: boolean }): Promise<DailyStandup> {
    const { data } = await this.client.post(`/api/v1/startups/${startupId}/standups/evening`, payload);
    return data;
  }

  async getTodayStandup(startupId: string): Promise<StandupStatus> {
    const { data } = await this.client.get(`/api/v1/startups/${startupId}/standups/today`);
    return data;
  }

  // === GROWTH ENGINE ===
  async getLeads(startupId: string): Promise<Lead[]> {
    const { data } = await this.client.get(`/api/v1/growth/leads?startupId=${startupId}`);
    return data;
  }

  async updateLead(id: string, updates: Partial<Lead>): Promise<Lead> {
    const { data } = await this.client.patch(`/api/v1/growth/leads/${id}`, updates);
    return data;
  }

  async createLead(lead: Partial<Lead>): Promise<Lead> {
    const { data } = await this.client.post('/api/v1/growth/leads', lead);
    return data;
  }

  // === METRICS ===
  async submitEngagementMetrics(startupId: string, payload: EngagementMetrics) {
    await this.client.post(`/api/v1/startups/${startupId}/metrics/engagement`, payload);
  }

  async submitFinancialMetrics(startupId: string, payload: FinancialMetrics) {
    await this.client.post(`/api/v1/startups/${startupId}/metrics/financial`, payload);
  }

  // === INVESTMENT ===
  async getInvestmentDashboard(): Promise<InvestmentDashboardItem[]> {
    const { data } = await this.client.get('/api/v1/investment/dashboard');
    return Array.isArray(data) ? data : [];
  }

  // === LEADERBOARD ===
  async getLeaderboard(params?: { category?: string; time_period?: string }): Promise<{ leaderboard: any[] }> {
    try {
      const { data } = await this.client.get('/api/v1/leaderboard', { params });
      return { leaderboard: data.leaderboard || data || [] };
    } catch (error) {
      console.error('Leaderboard API error:', error);
      return { leaderboard: [] };
    }
  }

  // === AMBASSADOR PROGRAM ===
  async getAmbassadorProfile(): Promise<AmbassadorProfileResponse> {
    const { data } = await this.client.get('/api/v1/ambassadors/me');
    return data;
  }

  async getAmbassadorConversions(skip = 0, limit = 20) {
    const { data } = await this.client.get('/api/v1/ambassadors/conversions', { params: { skip, limit } });
    return data;
  }

  async getAmbassadorEarnings() {
    const { data } = await this.client.get('/api/v1/ambassadors/earnings');
    return data;
  }

  async applyAmbassador(payload: any) {
    const { data } = await this.client.post('/api/v1/ambassadors/apply', payload);
    return data;
  }

  async stripeOnboard() {
    const { data } = await this.client.post('/api/v1/ambassadors/stripe/onboard');
    return data;
  }

  async requestPayout() {
    const { data } = await this.client.post('/api/v1/ambassadors/payout');
    return data;
  }

  // === REFERRAL PROGRAM ===
  async getReferralStats(): Promise<ReferralStatsResponse> {
    const { data } = await this.client.get('/api/v1/referrals/stats');
    return data;
  }

  async generateReferralLink() {
    const { data } = await this.client.post('/api/v1/referrals/generate-link');
    return data;
  }

  async getReferralLeaderboard(limit = 10) {
    const { data } = await this.client.get('/api/v1/referrals/leaderboard', { params: { limit } });
    return data;
  }
}

export const api = new ApiClient();
export default api;
