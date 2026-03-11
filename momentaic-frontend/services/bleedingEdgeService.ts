
import { GoogleGenAI, Type, Schema, HarmCategory, HarmBlockThreshold } from "@google/genai";
import { StorageService } from './storage';
import { QuantumState, MarketNarrative, IntegrationDiscovery } from '../types';

const MODEL_PRO = 'gemini-3-pro-preview';
const MODEL_FLASH = 'gemini-2.5-flash';

const SAFETY_SETTINGS = [
    { category: HarmCategory.HARM_CATEGORY_HARASSMENT, threshold: HarmBlockThreshold.BLOCK_ONLY_HIGH },
];

const getAI = async () => {
    let apiKey = process.env.API_KEY;
    const user = StorageService.getUser();
    if (user?.apiMode === 'PERSONAL' && user.personalApiKey) {
        apiKey = user.personalApiKey;
    }
    if (!apiKey) throw new Error("API_KEY_MISSING");
    return new GoogleGenAI({ apiKey });
};

// --- MOBY AUTONOMOUS: QUANTUM STATE ENGINE ---

export const analyzeQuantumState = async (customerContext: string): Promise<QuantumState[]> => {
    const ai = await getAI();
    const schema: Schema = {
        type: Type.ARRAY,
        items: {
            type: Type.OBJECT,
            properties: {
                dimension: { type: Type.STRING },
                status: { type: Type.STRING, enum: ["COHERENT", "ENTANGLED", "SUPERPOSITION"] },
                probability: { type: Type.NUMBER },
                insight: { type: Type.STRING }
            },
            required: ["dimension", "status", "probability", "insight"]
        }
    };

    const prompt = `
        Analyze the 'Quantum Customer State' for this context: "${customerContext}".
        Dimensions to analyze: Digital Behavior, Emotional State, Intent Probability, Social Influence.
        
        Definitions:
        - COHERENT: Clear, observable, stable signal.
        - ENTANGLED: Dependent on external factors/competitors.
        - SUPERPOSITION: Undecided, multiple potential outcomes simultaneously.
        
        Provide 4-5 dimensions with probability scores (0-1).
    `;

    try {
        const response = await ai.models.generateContent({
            model: MODEL_PRO,
            contents: prompt,
            config: {
                responseMimeType: "application/json",
                responseSchema: schema,
                safetySettings: SAFETY_SETTINGS
            }
        });
        return JSON.parse(response.text || "[]");
    } catch (e) {
        console.error("Quantum Analysis Failed", e);
        return [];
    }
};

export const runIntegrationSpider = async (domain: string): Promise<IntegrationDiscovery[]> => {
    // Note: In a real environment, verify legal compliance before scanning domains.
    await new Promise(resolve => setTimeout(resolve, 2000));

    const commonPlatforms = [
        { platform: "Salesforce API", type: 'API', impact: "High-value CRM sync" },
        { platform: "HubSpot Webhooks", type: 'WEBHOOK', impact: "Real-time event triggers" },
        { platform: "Segment Stream", type: 'HIDDEN_ENDPOINT', impact: "Raw behavioral data" },
        { platform: "Stripe Payments", type: 'API', impact: "Revenue operations" }
    ];

    return commonPlatforms.map((p, i) => ({
        id: `int_${Date.now()}_${i}`,
        platform: p.platform,
        type: p.type as any,
        status: 'DISCOVERED',
        potentialImpact: p.impact
    }));
};

// --- LEMLIST DOMINATION: REALITY MANIPULATOR ---

export const generateMarketNarrative = async (competitor: string, goal: string): Promise<MarketNarrative[]> => {
    const ai = await getAI();
    const schema: Schema = {
        type: Type.ARRAY,
        items: {
            type: Type.OBJECT,
            properties: {
                id: { type: Type.STRING },
                topic: { type: Type.STRING },
                currentSentiment: { type: Type.STRING },
                targetSentiment: { type: Type.STRING },
                strategy: { type: Type.STRING },
                tactics: { type: Type.ARRAY, items: { type: Type.STRING } }
            },
            required: ["id", "topic", "currentSentiment", "targetSentiment", "strategy", "tactics"]
        }
    };

    const prompt = `
        Act as a 'Market Reality Manipulator'.
        Competitor: ${competitor}
        Goal: ${goal}
        
        Generate 3 'Conversation Hijacking' strategies to shift market perception.
        Focus on 'Narrative Seeding' and 'Category Redefinition'.
    `;

    try {
        const response = await ai.models.generateContent({
            model: MODEL_PRO,
            contents: prompt,
            config: {
                responseMimeType: "application/json",
                responseSchema: schema,
                safetySettings: SAFETY_SETTINGS
            }
        });
        return JSON.parse(response.text || "[]");
    } catch (e) {
        console.error("Narrative Gen Failed", e);
        return [];
    }
};
