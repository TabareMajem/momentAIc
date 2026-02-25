
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
      if (typeof window !== 'undefined') {
        const lang = localStorage.getItem('i18nextLng') || 'en';
        config.headers['Accept-Language'] = lang;
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

  async firebaseLogin(idToken: string): Promise<AuthResponse> {
    const { data } = await this.client.post('/api/v1/auth/firebase-oauth', { id_token: idToken });
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

  async forgotPassword(email: string): Promise<{ message: string }> {
    const { data } = await this.client.post('/api/v1/auth/forgot-password', { email });
    return data;
  }

  async resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
    const { data } = await this.client.post('/api/v1/auth/reset-password', { token, new_password: newPassword });
    return data;
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

  async importFromSource(url: string, sourceType: 'github' | 'web' | 'doc' = 'github'): Promise<any> {
    const { data } = await this.client.post('/api/v1/startups/import', {
      url,
      source_type: sourceType,
      extra_data: {}
    });
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

  async getDashboard(startupId: string): Promise<any> {
    const { data } = await this.client.get(`/api/v1/startups/${startupId}/dashboard`);
    return data;
  }

  async getBenchmarks(startupId: string) {
    const { data } = await this.client.get(`/api/v1/startups/${startupId}/benchmarks`);
    return data;
  }

  // === MOMENTUM OS ===
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

  async triggerCompetitorMonitor(startupId: string, knownCompetitors: string[] = []): Promise<any> {
    const { data } = await this.client.post('/api/v1/agents/competitor/monitor', {
      startup_id: startupId,
      known_competitors: knownCompetitors
    });
    return data;
  }

  async triggerSalesHunt(startupId: string): Promise<any> {
    const { data } = await this.client.post('/api/v1/agents/sales/hunt', {
      startup_id: startupId
    });
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
      if (typeof window !== 'undefined') {
        const lang = localStorage.getItem('i18nextLng') || 'en';
        headers['Accept-Language'] = lang;
      }
      if (typeof window !== 'undefined') {
        const lang = localStorage.getItem('i18nextLng') || 'en';
        headers['Accept-Language'] = lang;
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

  async submitAgentFeedback(payload: { startup_id: string; agent_type: string; message_id?: string; is_positive: boolean; feedback_text?: string }) {
    const { data } = await this.client.post('/api/v1/agents/feedback', payload);
    return data;
  }

  async getCrossStartupInsights(startupId: string, limit: number = 5) {
    const { data } = await this.client.get(`/api/v1/intelligence/cross-startup`, {
      params: { startup_id: startupId, limit }
    });
    return data;
  }

  // === PLAYBOOKS ===
  async getIndustryPlaybooks(industry?: string) {
    const { data } = await this.client.get('/api/v1/playbooks', {
      params: { industry }
    });
    return data;
  }

  // === MARKETPLACE ===
  async getMarketplaceTemplates(industry?: string, agentType?: string, sortBy: 'upvotes' | 'newest' = 'upvotes') {
    const { data } = await this.client.get('/api/v1/marketplace/templates', {
      params: { industry, agent_type: agentType, sort_by: sortBy }
    });
    return data;
  }

  async upvoteTemplate(templateId: string) {
    const { data } = await this.client.post(`/api/v1/marketplace/templates/${templateId}/upvote`);
    return data;
  }

  async cloneTemplate(templateId: string) {
    const { data } = await this.client.post(`/api/v1/marketplace/templates/${templateId}/clone`);
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

  // === SOCIAL & GENIUS ONBOARDING ===

  // Social OAuth
  async getOAuthStatus() {
    const { data } = await this.client.get('/api/v1/auth/oauth/status');
    return data;
  }

  async connectSocial(platform: 'twitter' | 'linkedin', startupId: string) {
    const { data } = await this.client.get(`/api/v1/social/connect/${platform}?startup_id=${startupId}`);
    return data; // Returns { auth_url: string }
  }

  // Genius Genius Agent
  async startGeniusSession(url: string, startupId?: string) {
    const { data } = await this.client.post('/api/v1/onboarding/genius/start', { url, startup_id: startupId });
    return data;
  }

  async continueGeniusChat(message: string) {
    const { data } = await this.client.post('/api/v1/onboarding/genius/chat', { message });
    return data;
  }

  async executeGeniusPlan(startupId: string, plan: any) {
    const { data } = await this.client.post('/api/v1/onboarding/genius/execute', { startup_id: startupId, plan });
    return data;
  }

  // === GUERRILLA GROWTH ===
  async scanOpportunities(platform: string, keywords: string) {
    const { data } = await this.client.post('/api/v1/guerrilla/scan', { platform, keywords });
    return data;
  }

  async scanReddit(keywords: string[]) {
    const { data } = await this.client.post('/api/v1/guerrilla/scan', { platform: 'reddit', keywords: keywords.join(',') });
    return data;
  }

  async interceptTwitter(competitors: string[]) {
    const { data } = await this.client.post('/api/v1/guerrilla/scan', { platform: 'twitter', keywords: competitors.join(',') });
    return data;
  }

  async surfTrends() {
    const { data } = await this.client.post('/api/v1/guerrilla/scan', { platform: 'general', keywords: 'latest trends' });
    return data;
  }

  // === GROWTH ENGINE ===
  async generateOutreach(startupId: string, leadId: string, options: { channel: string; tone?: string; objective?: string; custom_context?: string }) {
    const { data } = await this.client.post(`/api/v1/growth/leads/${leadId}/generate-outreach?startup_id=${startupId}`, options);
    return data;
  }

  async generateContent(payload: any) {
    const { data } = await this.client.post('/api/v1/growth/content/generate', payload);
    return data;
  }

  async getViralHistory() {
    const { data } = await this.client.get('/api/v1/viral/history');
    return data;
  }

  async generateViralCampaign(topic: string) {
    const { data } = await this.client.post('/api/v1/viral/generate', { topic });
    return data;
  }

  async deployGlobalCampaign(payload: { domain: string; personas: string[]; languages: string[]; additional_context?: string }) {
    const { data } = await this.client.post('/api/v1/campaigns/global/deploy', payload);
    return data;
  }

  async createViralCampaign(payload: {
    campaign_type: string;
    target_audience?: string;
    tone?: string;
    variations?: number;
    platform?: string;
    additional_context?: any;
    startup_id: string; // convenient to pass here, though API expects it in query or path if needed, but here it's likely part of the body or context
  }) {
    // Note: The backend endpoint is /api/v1/growth/campaigns/viral
    // And it expects startup_id as query param ?startup_id=... based on other endpoints pattern
    const { startup_id, ...body } = payload;
    const { data } = await this.client.post(`/api/v1/growth/campaigns/viral?startup_id=${startup_id}`, body);
    return data;
  }

  // === GROWTH ANALYTICS ===
  async getEmpireStatus() {
    const { data } = await this.client.get('/api/v1/growth-analytics/empire-status');
    return data;
  }

  async updateEmpireStep(step: number, metadata: any = {}, complete: boolean = false) {
    const { data } = await this.client.post('/api/v1/growth-analytics/empire-step', {
      step,
      metadata,
      complete
    });
    return data;
  }

  // === INNOVATOR LAB ===
  async triggerDeepResearch(topic: string, depth: number = 3) {
    const { data } = await this.client.post('/api/v1/innovator/deep-research', { topic, depth });
    return data;
  }

  // === AGENTFORGE INTEGRATION ===
  async triggerVoiceAgent(text: string, action: string = "call_me") {
    const { data } = await this.client.post('/api/v1/integrations/agentforge/trigger-voice', { text, action });
    return data;
  }

  // === QWEN-TTS VOICE ===
  /**
   * Synthesize text to speech
   * Returns a Blob url that can be played by Audio element
   */
  async speak(text: string, voiceId?: string): Promise<string> {
    const response = await this.client.post('/api/v1/voice/speak',
      { text, voice_id: voiceId },
      { responseType: 'blob' }
    );
    return URL.createObjectURL(response.data);
  }
  // === OPERATIONS / PULSE ===
  async getPulse(startupId: string) {
    const { data } = await this.client.get(`/api/v1/a2a/pulse/${startupId}`);
    return data;
  }

  async getPulseTimeline(startupId: string, params: any) {
    const { data } = await this.client.get(`/api/v1/a2a/pulse/${startupId}/timeline`, { params });
    return data;
  }

  async runOperationsMission(mission: string, context: any, startupId: string) {
    // Expected endpoint: POST /api/v1/operations/mission
    const { data } = await this.client.post(`/api/v1/operations/mission`, {
      mission,
      context,
      startup_id: startupId
    });
    return data;
  }
  // === PRODUCT FACTORY ===
  async runProductMission(mission: string, requirement: any, startupId: string) {
    // Expected endpoint: POST /api/v1/product/mission
    const { data } = await this.client.post(`/api/v1/product/mission`, {
      mission,
      requirement,
      startup_id: startupId
    });
    return data;
  }

  // === ASTROTURF COMMUNITY GTM ===
  async getAstroTurfMentions(startupId: string) {
    const { data } = await this.client.get(`/api/v1/astroturf/mentions?startup_id=${startupId}`);
    return data;
  }

  async deployAstroTurfMention(mentionId: string) {
    const { data } = await this.client.post(`/api/v1/astroturf/mentions/${mentionId}/deploy`);
    return data;
  }

  async dismissAstroTurfMention(mentionId: string) {
    const { data } = await this.client.post(`/api/v1/astroturf/mentions/${mentionId}/dismiss`);
    return data;
  }

  // === AGENTFORGE / YOKAIZEN CORE ===
  async getYokaizenAgents() {
    const { data } = await this.client.get(`/api/v1/integrations/yokaizen/agents/me`);
    return data;
  }

  async importYokaizenAgent(agentId: string) {
    const { data } = await this.client.post(`/api/v1/integrations/yokaizen/agents/${agentId}/import`);
    return data;
  }

  // === TELECOM / TWILIO ===
  async searchTelecomNumbers(accountSid: string, authToken: string, areaCode: string) {
    const { data } = await this.client.post(`/api/v1/voice/webhooks/telecom/search`, null, {
      params: { account_sid: accountSid, auth_token: authToken, area_code: areaCode }
    });
    return data;
  }

  async provisionTelecomNumber(accountSid: string, authToken: string, phoneNumber: string, startupId: string, language: string = 'en-US') {
    const { data } = await this.client.post(`/api/v1/voice/webhooks/telecom/provision`, null, {
      params: { account_sid: accountSid, auth_token: authToken, phone_number: phoneNumber, startup_id: startupId, language }
    });
    return data;
  }

  async getProvisionedNumbers(startupId: string) {
    const { data } = await this.client.get(`/api/v1/voice/webhooks/telecom/numbers`, {
      params: { startup_id: startupId }
    });
    return data;
  }

  // === AGENTFORGE OUTBOUND PROXY ===
  async triggerAgentForgeWorkflow(triggerUrl: string, payload: any) {
    const { data } = await this.client.post(`/api/v1/integrations/agentforge/trigger-workflow`, {
      trigger_url: triggerUrl,
      payload
    });
    return data;
  }

  async triggerDirectAgentForge(agentType: string, payload: any) {
    const { data } = await this.client.post(`/api/v1/integrations/agentforge/direct-agent`, {
      agent_type: agentType,
      payload
    });
    return data;
  }

  // === KILL SHOT: SHOW ME THE MONEY ===
  async getLiveRevenue(startupId: string) {
    const { data } = await this.client.get(`/api/v1/startups/${startupId}/live-revenue`);
    return data;
  }

  // === KILL SHOT: AGENT COMPOSABILITY DAG ===
  async executeAgentDAG(startupId: string, dag: { nodes: any[]; edges: any[]; initial_input: string }) {
    const { data } = await this.client.post(`/api/v1/startups/${startupId}/execute-dag`, dag);
    return data;
  }

  // === KILL SHOT: MAGIC URL DEMO (60-SECOND) ===
  async runMagicDemo(url: string) {
    const { data } = await this.client.post(`/api/v1/onboarding/magic-demo`, { url });
    return data;
  }
}

export const api = new ApiClient();
export default api;
