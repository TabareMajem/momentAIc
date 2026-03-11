import api from './api';
import { UserProfile, SniperTarget, Lead, ContentPiece } from '../types';

export const BackendService = {
    API_URL: import.meta.env.VITE_YOKAIZEN_API_URL || '/yokaizen-api',

    // --- AUTH ---
    login: async (email: string, password: string) => {
        const response = await api.post('/auth/login', { email, password });
        if (response.data.token) {
            // Store token and user in localStorage for persistence
            // We adapt the backend user object to the frontend UserProfile interface
            const user = { ...response.data.user, token: response.data.token };
            localStorage.setItem('yokaizen_session', JSON.stringify(user));
            window.dispatchEvent(new Event('user-update'));
            return { success: true, user };
        }
        return { success: false, message: 'Login failed' };
    },

    register: async (name: string, email: string, password: string) => {
        const response = await api.post('/auth/register', { name, email, password });
        if (response.data.token) {
            const user = { ...response.data.user, token: response.data.token };
            localStorage.setItem('yokaizen_session', JSON.stringify(user));
            window.dispatchEvent(new Event('user-update'));
            return { success: true, user };
        }
        return { success: false, message: 'Registration failed' };
    },

    logout: () => {
        localStorage.removeItem('yokaizen_session');
        window.dispatchEvent(new Event('user-update'));
    },

    refreshProfile: async () => {
        try {
            const response = await api.get('/auth/me');
            if (response.data) {
                const stored = localStorage.getItem('yokaizen_session');
                const token = stored ? JSON.parse(stored).token : null;
                if (token) {
                    const updatedUser = { ...response.data, token };
                    localStorage.setItem('yokaizen_session', JSON.stringify(updatedUser));
                    window.dispatchEvent(new Event('user-update'));
                    return updatedUser;
                }
            }
        } catch (e) {
            console.error('Failed to refresh profile', e);
        }
    },

    // --- SNIPER ---
    createTarget: async (target: Partial<SniperTarget>) => {
        const response = await api.post('/sniper/targets', target);
        return response.data;
    },

    sniperBulkUpload: async (file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post('/sniper/targets/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        return response.data;
    },

    getTargets: async () => {
        const response = await api.get('/sniper/targets');
        return response.data;
    },

    deleteTarget: async (id: string) => {
        const response = await api.delete(`/sniper/targets/${id}`);
        return response.data;
    },

    generateIcebreaker: async (targetId: string) => {
        const response = await api.post(`/sniper/generate/${targetId}`);
        return response.data;
    },

    getLeads: async () => {
        const response = await api.get('/gatekeeper/leads');
        return response.data;
    },

    analyzeLead: async (leadId: string) => {
        const response = await api.post(`/gatekeeper/analyze/${leadId}`);
        return response.data;
    },

    archiveLead: async (leadId: string) => {
        const response = await api.post(`/gatekeeper/archive/${leadId}`);
        return response.data;
    },

    replyToLead: async (leadId: string, message?: string) => {
        const response = await api.post(`/gatekeeper/reply/${leadId}`, { message });
        return response.data;
    },

    // --- CONTENT ---
    getContentHistory: async () => {
        const response = await api.get('/content/history');
        return response.data;
    },

    generateContent: async (prompt: string, type: string) => {
        const response = await api.post('/content/generate', { prompt, type });
        return response.data;
    },

    // --- MEDIA ---
    generateVideo: async (prompt: string) => {
        const response = await api.post('/media/video/generate', { prompt });
        return response.data; // { jobId }
    },

    getVideoStatus: async (jobId: string) => {
        const response = await api.get(`/media/video/status/${jobId}`);
        return response.data;
    },

    generateImage: async (prompt: string) => {
        const response = await api.post('/media/image/generate', { prompt });
        return response.data;
    },

    generateAvatarImage: async (productImageBase64: string, characterImageBase64: string, prompt: string) => {
        const response = await api.post('/media/avatar/generate-image', { productImageBase64, characterImageBase64, prompt });
        return response.data;
    },

    generateAvatarVideo: async (imageBase64: string, prompt: string, model: 'VEO' | 'KLING' | 'SEEDANCE') => {
        const response = await api.post('/media/avatar/generate-video', { imageBase64, prompt, model });
        return response.data;
    },

    getAvatarVideoStatus: async (taskId: string, model: string) => {
        const response = await api.get(`/media/avatar/video-status/${taskId}?model=${model}`);
        return response.data;
    },


    // --- VIRAL ---
    generateViralStrategy: async (url: string, budget: string, timeline: string) => {
        const response = await api.post('/viral/strategy', { url, budget, timeline });
        return response.data; // { jobId }
    },

    getViralStrategyStatus: async (jobId: string) => {
        const response = await api.get(`/viral/strategy/status/${jobId}`);
        return response.data;
    },

    getViralHistory: async () => {
        const response = await api.get('/viral/history');
        return response.data;
    },
    // --- GTM AGENT ---
    uploadGTMDoc: async (file: File) => {
        const formData = new FormData();
        formData.append('document', file);
        const response = await api.post('/gtm/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        return response.data;
    },

    executeCampaignTask: async (taskId: string) => {
        const response = await api.post(`/gtm/execute/${taskId}`);
        return response.data;
    },

    getViralTrends: async (subreddit: string) => {
        const response = await api.get(`/viral/trends?subreddit=${subreddit}`);
        return response.data;
    },

    generateViralScripts: async (trends: any[], subreddit: string) => {
        const response = await api.post('/viral/scripts', { trends, subreddit });
        return response.data;
    },

    analyzeViralVideo: async (file: File) => {
        const formData = new FormData();
        formData.append('video', file);
        const response = await api.post('/viral/analyze-video', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        return response.data;
    },

    // --- Workflow ---
    getWorkflows: async () => {
        const response = await api.get('/workflow');
        return response.data;
    },

    saveWorkflow: async (workflow: any) => {
        const response = await api.post('/workflow', workflow);
        return response.data;
    },

    // --- Growth ---
    enrichData: async (rowData: any, prompt: string) => {
        const response = await api.post('/growth/enrich', { rowData, prompt });
        return response.data;
    },

    // --- BILLING ---
    createCheckoutSession: async (priceId: string, mode: 'payment' | 'subscription') => {
        const response = await api.post('/billing/create-checkout', { priceId, mode });
        return response.data; // { url }
    },

    // --- ADMIN ---
    getUsers: async () => {
        const response = await api.get('/admin/users');
        return response.data;
    },

    updateUser: async (id: string, data: any) => {
        const response = await api.put(`/admin/users/${id}`, data);
        return response.data;
    },

    deleteUser: async (id: string) => {
        const response = await api.delete(`/admin/users/${id}`);
        return response.data;
    },

    getSystemStats: async () => {
        const response = await api.get('/admin/stats');
        return response.data;
    },

    getActivityStats: async () => {
        const response = await api.get('/admin/activity');
        return response.data;
    },

    getSocialConnections: async () => {
        const response = await api.get('/social/connections');
        return response.data;
    },

    // --- LEGAL ---
    reviewContract: async (contractText: string, filename?: string) => {
        const response = await api.post('/legal/review', { contractText, filename });
        return response.data;
    },

    // --- RECRUITING ---
    analyzeCandidate: async (name: string, resumeText: string, jobDescription?: string) => {
        const response = await api.post('/recruiting/analyze', { name, resumeText, jobDescription });
        return response.data;
    },

    getCandidates: async () => {
        const response = await api.get('/recruiting/candidates');
        return response.data;
    },

    // --- SUPPORT ---
    answerSupportQuery: async (query: string, history?: any[], contextUrl?: string) => {
        const response = await api.post('/support/query', { query, history, contextUrl });
        return response.data;
    },

    // --- MOBY ---
    runMobyAnalysis: async (segmentData: any, timeframe: string, useStripe: boolean = false) => {
        const response = await api.post('/moby/analyze', { segmentData, timeframe, useStripe });
        return response.data;
    },



    analyzeQuantumState: async (context: string) => {
        const response = await api.post('/moby/quantum', { context });
        return response.data;
    },

    runIntegrationSpider: async (domain: string) => {
        const response = await api.post('/moby/spider', { domain });
        return response.data;
    },

    // --- LEMLIST ---
    generateMarketNarrative: async (competitor: string, goal: string) => {
        const response = await api.post('/lemlist/generate', { competitor, goal });
        return response.data;
    },

    // --- PROCUREMENT ---
    auditInvoice: async (fileOrData: File | any) => {
        if (fileOrData instanceof File) {
            const formData = new FormData();
            formData.append('invoice', fileOrData);
            const response = await api.post('/procurement/audit', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            return response.data;
        } else {
            const response = await api.post('/procurement/audit', { invoiceData: fileOrData });
            return response.data;
        }
    },

    // --- ONBOARDING ---
    generateOnboardingSample: async (companyUrl: string, goal: string) => {
        try {
            const response = await api.post('/content/onboarding-sample', { companyUrl, goal });
            return response.data;
        } catch (e) {
            // Fallback: Generate locally if endpoint doesn't exist yet
            const domain = companyUrl.replace('https://', '').replace('http://', '').split('/')[0];
            return {
                hooks: [
                    `Stop wasting time on cold calls. Here's how ${domain} can 10x outreach.`,
                    `The secret to finding your ideal customers? AI agents. No sales team needed.`,
                    `Why top founders are switching to autonomous sales. The future is here.`
                ],
                analysis: `Based on ${domain}, you're in a competitive space. Your first mission: run a Sniper scan to find 50 high-intent leads.`
            };
        }
    },

    startGodMode: async (url: string, goal: string) => {
        const response = await api.post('/growth/god-mode', { url, goal });
        return response.data;
    },

    // --- VIRAL SHARING ---
    generateShareLink: async (strategyId: string) => {
        const response = await api.post('/viral/share', { strategyId });
        return response.data;
    },

    // --- CAMPAIGNS ---
    getCampaignProjects: async () => {
        const response = await api.get('/campaigns/projects');
        return response.data;
    },

    createCampaignProject: async (project: { name: string; domain: string; description?: string }) => {
        const response = await api.post('/campaigns/projects', project);
        return response.data;
    },

    getCampaigns: async (projectId: string) => {
        const response = await api.get(`/campaigns/projects/${projectId}/campaigns`);
        return response.data;
    },

    createCampaign: async (projectId: string, data: { name: string; strategyDocUrl?: string }) => {
        const response = await api.post(`/campaigns/projects/${projectId}/campaigns`, data);
        return response.data;
    },

    updateCampaignStatus: async (campaignId: string, status: string) => {
        const response = await api.patch(`/campaigns/campaigns/${campaignId}/status`, { status });
        return response.data;
    },

    parseCampaignStrategy: async (campaignId: string, strategyText: string) => {
        const response = await api.post(`/campaigns/campaigns/${campaignId}/parse`, { strategyText });
        return response.data;
    },


    recordCampaignMetric: async (campaignId: string, name: string, value: number) => {
        const response = await api.post(`/campaigns/campaigns/${campaignId}/metrics`, { name, value });
        return response.data;
    }
};
