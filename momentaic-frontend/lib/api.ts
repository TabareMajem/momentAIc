
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


  // === INTEGRATIONS ===
  async getIntegrations(startupId: string) {
    const { data } = await this.client.get(`/api/v1/integrations?startup_id=${startupId}`);
    return data;
  }

  async connectIntegration(startupId: string, payload: any) {
    const { data } = await this.client.post(`/api/v1/integrations?startup_id=${startupId}`, payload);
    return data;
  }

  async disconnectIntegration(startupId: string, integrationId: string) {
    const { data } = await this.client.delete(`/api/v1/integrations/${integrationId}?startup_id=${startupId}`);
    return data;
  }

  async syncIntegration(startupId: string, integrationId: string, dataTypes?: string[]) {
    const { data } = await this.client.post(`/api/v1/integrations/${integrationId}/sync?startup_id=${startupId}`, { data_types: dataTypes });
    return data;
  }

  // === MARKETPLACE ===
  async getMarketplaceTools(category?: string) {
    const { data } = await this.client.get('/api/v1/marketplace/tools' + (category ? `?category=${category}` : ''));
    return data;
  }

  async submitMarketplaceTool(payload: any) {
    const { data } = await this.client.post('/api/v1/marketplace/submit', payload);
    return data;
  }

  async installMarketplaceTool(startupId: string, toolId: string) {
    const { data } = await this.client.post(`/api/v1/marketplace/install/${toolId}?startup_id=${startupId}`);
    return data;
  }

  // === ONBOARDING ===
  async createCheckoutSession(tier: string): Promise<{ url?: string; success?: boolean }> {
    const { data } = await this.client.post('/api/v1/billing/checkout', { tier });
    return data;
  }

  async analyzeStartup(description: string): Promise<{
    industry: string;
    stage: string;
    follow_up_question: string;
    summary: string;
    potential_competitors: string[];
    insight: string;
  }> {
    const { data } = await this.client.post('/api/v1/onboarding/analyze', { description });
    return data;
  }

  async importAppFromGithub(repoUrl: string): Promise<any> {
    const { data } = await this.client.post('/api/v1/startups/import/github', { repo_url: repoUrl });
    return data;
  }

  /**
   * Stream instant analysis via SSE for WOW onboarding
   */
  async streamInstantAnalysis(
    description: string,
    callbacks: {
      onProgress?: (data: { step: string; message: string; percent: number }) => void;
      onCompetitor?: (data: { name: string; url: string; description: string }) => void;
      onInsight?: (data: { industry: string; stage: string; summary: string; insight: string; follow_up_question: string }) => void;
      onComplete?: (report: any) => void;
      onError?: (error: string) => void;
    }
  ): Promise<void> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const url = `${API_URL}/api/v1/startups/instant-analysis`;
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify({ description }),
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('No response body');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonStr = line.slice(6);
            try {
              const parsed = JSON.parse(jsonStr);
              const { event, data } = parsed;

              switch (event) {
                case 'progress':
                  callbacks.onProgress?.(data);
                  break;
                case 'competitor':
                  callbacks.onCompetitor?.(data);
                  break;
                case 'insight':
                  callbacks.onInsight?.(data);
                  break;
                case 'complete':
                  callbacks.onComplete?.(data.report);
                  break;
                case 'error':
                  callbacks.onError?.(data.message);
                  break;
              }
            } catch (e) {
              console.warn('Failed to parse SSE:', jsonStr);
            }
          }
        }
      }
    } catch (error: any) {
      callbacks.onError?.(error.message || 'Unknown error');
    }
  }

  async generateDayOnePack(): Promise<any> {
    const { data } = await this.client.post('/api/v1/vault/generate-day-one');
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

  async streamChatWithAgent(
    request: AgentChatRequest,
    onToken: (token: string) => void,
    onComplete?: (fullText: string) => void,
    onError?: (err: any) => void
  ): Promise<void> {
    try {
      const token = this.getToken();
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      // Use fetch for streaming support (Axios is bad at this)
      // Construct full URL properly
      const baseUrl = API_URL || window.location.origin; // Fallback if API_URL is relative
      // If API_URL is relative (empty string), fetch handles it relative to current origin.
      // If it's absolute, it works.
      const url = `${API_URL}/api/v1/agents/chat/stream`;

      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`Stream failed: ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('No response body');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullText = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        // Parse SSE format: "data: {...}\n\n"
        const lines = chunk.split('\n\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonStr = line.slice(6);
            if (jsonStr === '[DONE]') continue;

            try {
              const data = JSON.parse(jsonStr);
              if (data.token) {
                onToken(data.token);
                fullText += data.token;
              }
              // Handle other event types if needed (e.g., tool_use)
            } catch (e) {
              console.warn('Failed to parse SSE data:', jsonStr);
            }
          }
        }
      }

      if (onComplete) {
        onComplete(fullText);
      }

    } catch (error) {
      console.error('Streaming chat error:', error);
      if (onError) onError(error);
    }
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
