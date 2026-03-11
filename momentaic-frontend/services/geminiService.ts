
import api from './api';

// --- AGENT FUNCTIONS ---

export const generateIcebreaker = async (profileText: string, targetName: string): Promise<string> => {
    try {
        const targetRes = await api.post('/sniper/targets', {
            name: targetName,
            linkedinUrl: 'https://linkedin.com/in/unknown',
            rawProfileText: profileText
        });
        const targetId = targetRes.data.id;

        const res = await api.post(`/sniper/generate/${targetId}`);
        return res.data.icebreaker || "Could not generate icebreaker.";
    } catch (error: any) {
        console.error("Icebreaker error:", error);
        return `Error: ${error.message}`;
    }
};

export const analyzeLead = async (message: string, name: string) => {
    try {
        const leadRes = await api.post('/gatekeeper/inbound', {
            name,
            email: 'unknown@example.com',
            message,
            userId: 'temp-user'
        });

        if (leadRes.data.id) {
            const analysisRes = await api.post(`/gatekeeper/analyze/${leadRes.data.id}`);
            return analysisRes.data.analysisResult || {};
        }
        return {};
    } catch (error) {
        console.error("Analyze Lead error:", error);
        return {};
    }
};

export const repurposeContent = async (rawIdea: string) => {
    try {
        const res = await api.post('/content/generate', { rawIdea });
        return res.data;
    } catch (error) {
        console.error("Repurpose content error:", error);
        return {};
    }
};

export const generateSocialImage = async (prompt: string): Promise<string | null> => {
    try {
        const res = await api.post('/media/image/generate', { prompt });
        return res.data.imageUrl || null;
    } catch (error) {
        console.error("Generate Image error:", error);
        return null;
    }
};

export const editImage = async (base64Image: string, prompt: string): Promise<string | null> => {
    try {
        const res = await api.post('/media/image/edit', { base64Image, prompt });
        return res.data.imageUrl || null;
    } catch (error) {
        console.error("Edit Image error:", error);
        return null;
    }
};

export const generateVeoVideo = async (prompt: string, base64Image?: string, aspectRatio: '16:9' | '9:16' = '16:9'): Promise<string | null> => {
    try {
        const res = await api.post('/viral/video-gen', { prompt });
        return res.data.data?.generatedVideos?.[0]?.video?.uri || null;
    } catch (error) {
        console.error("Veo Video error:", error);
        return null;
    }
};

export const transcribeAudio = async (base64Audio: string, mimeType: string = 'audio/webm'): Promise<string> => {
    try {
        const res = await api.post('/media/audio/transcribe', { base64Audio, mimeType });
        return res.data.text || "Transcription failed.";
    } catch (error) {
        console.error("Transcribe error:", error);
        return "Transcription failed.";
    }
};

export const generateSpeech = async (text: string): Promise<string | null> => {
    try {
        const res = await api.post('/media/audio/tts', { text });
        return res.data.audioData || null;
    } catch (error) {
        console.error("TTS error:", error);
        return null;
    }
};

export const generateN8nWorkflow = async (description: string): Promise<string> => {
    try {
        const res = await api.post('/workflow/generate-n8n', { description });
        return JSON.stringify(res.data.workflow);
    } catch (error) {
        console.error("N8n error:", error);
        return "{}";
    }
};

export const performEnrichment = async (rowContext: Record<string, any>, instruction: string): Promise<string> => {
    try {
        const res = await api.post('/growth/enrich', { rowData: rowContext, prompt: instruction });
        return res.data.enrichedData || "No Data";
    } catch (error) {
        console.error("Enrichment error:", error);
        return "Error";
    }
};

export const analyzeCandidate = async (resumeInput: { type: 'text' | 'file', content: string }, jobDescription: string) => {
    try {
        const res = await api.post('/recruiting/analyze', {
            name: 'Unknown Candidate',
            resumeText: resumeInput.content,
            jobDescription
        });
        return res.data.analysis || {};
    } catch (error) {
        console.error("Candidate analysis error:", error);
        throw error;
    }
};

export const reviewContract = async (contractInput: { type: 'text' | 'file', content: string }) => {
    try {
        const res = await api.post('/legal/review', {
            contractText: contractInput.content,
            filename: 'contract_review.pdf'
        });
        return res.data.analysis || [];
    } catch (error) {
        console.error("Contract review error:", error);
        throw error;
    }
};

export const answerSupportQuery = async (query: string, knowledgeBase: string, url?: string) => {
    try {
        const res = await api.post('/support/query', {
            query,
            history: [],
            contextUrl: url
        });
        return res.data.answer;
    } catch (error) {
        console.error("Support query error:", error);
        throw error;
    }
};

export const auditInvoice = async (invoiceInput: { type: 'data' | 'file', content: any }) => {
    try {
        if (invoiceInput.type === 'file') {
            throw new Error("File audit not fully migrated yet");
        }

        const res = await api.post('/procurement/audit', { invoiceData: invoiceInput.content });
        return res.data.result;
    } catch (error) {
        console.error("Audit invoice error:", error);
        throw error;
    }
};

export const generateViralScriptsFromTrends = async (trendData: any, niche: string) => {
    try {
        const res = await api.post('/viral/scripts', { trends: trendData, subreddit: niche });
        return res.data;
    } catch (error) {
        console.error("Viral scripts error:", error);
        return [];
    }
};

export const analyzeVideoForViralScore = async (videoBase64: string, mimeType: string = "video/mp4") => {
    try {
        const res = await fetch(`${import.meta.env.VITE_API_URL}/viral/analyze-video`, {
            method: 'POST',
            body: JSON.stringify({ videoBase64 }),
        });
        return {};
    } catch (error) {
        console.error("Video analyze error:", error);
        throw error;
    }
};
