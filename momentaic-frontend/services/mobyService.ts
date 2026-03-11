
import { GoogleGenAI, Type, Schema, HarmCategory, HarmBlockThreshold } from "@google/genai";
import { StorageService } from './storage';
import { MobyMetrics, MobyInsight, MobyReport } from '../types';

// Using Pro model for deep analysis
const MODEL_PRO = 'gemini-3-pro-preview';
const MODEL_FLASH = 'gemini-2.5-flash';

const SAFETY_SETTINGS = [
    { category: HarmCategory.HARM_CATEGORY_HARASSMENT, threshold: HarmBlockThreshold.BLOCK_ONLY_HIGH },
];

// --- 1. DATA CONNECTION HUB (Simulation) ---
// Simulates connecting to Shopify, Meta, Klaviyo and pulling 30 days of data
export const connectDataSources = async (): Promise<MobyMetrics> => {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Generate realistic random DTC data (Simulating a $1M-$5M/yr brand)
    const revenue = Math.floor(Math.random() * (450000 - 150000) + 150000);
    const spend = Math.floor(revenue * (Math.random() * (0.40 - 0.20) + 0.20)); // 20-40% of rev
    const roas = parseFloat((revenue / spend).toFixed(2));
    const orders = Math.floor(revenue / 85);
    const aov = parseFloat((revenue / orders).toFixed(2));
    const cac = parseFloat((spend / (orders * 0.8)).toFixed(2)); // Assuming 80% new cust

    return {
        revenue,
        spend,
        roas,
        aov,
        cac,
        conversionRate: parseFloat((Math.random() * (3.5 - 1.5) + 1.5).toFixed(2))
    };
};

const getAI = async () => {
    let apiKey = process.env.API_KEY;
    const user = StorageService.getUser();
    if (user?.apiMode === 'PERSONAL' && user.personalApiKey) {
        apiKey = user.personalApiKey;
    } else {
        // @ts-ignore
        if (window.aistudio && window.aistudio.hasSelectedApiKey && !apiKey) {
            // In browser environment with injected key
        }
    }
    if (!apiKey) throw new Error("API_KEY_MISSING");
    return new GoogleGenAI({ apiKey });
};

// --- 2. SPECIALIZED SUB-AGENTS ---

const analyzeSegment = async (agentRole: string, promptContext: string, metrics: MobyMetrics): Promise<MobyInsight[]> => {
    const ai = await getAI();

    const schema: Schema = {
        type: Type.ARRAY,
        items: {
            type: Type.OBJECT,
            properties: {
                title: { type: Type.STRING },
                finding: { type: Type.STRING },
                recommendation: { type: Type.STRING },
                revenueImpact: { type: Type.NUMBER },
                priority: { type: Type.STRING, enum: ["HIGH", "MEDIUM", "LOW"] }
            },
            required: ["title", "finding", "recommendation", "revenueImpact", "priority"]
        }
    };

    const prompt = `
        You are Moby's ${agentRole}. 
        Analyze the following DTC Business Metrics: ${JSON.stringify(metrics)}.
        Context: ${promptContext}
        
        Generate 2 specific, high-impact insights/recommendations.
        Estimate the monthly revenue impact in USD conservatively.
        Focus on actionable steps.
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

        const insights = JSON.parse(response.text || "[]");
        // Inject category for UI filtering
        return insights.map((i: any) => ({ ...i, category: agentRole.split(' ')[0].toUpperCase() }));
    } catch (e) {
        console.error(`${agentRole} Error:`, e);
        return [];
    }
};

// --- 3. ORCHESTRATOR ---

export const runMobyAnalysis = async (metrics: MobyMetrics): Promise<MobyReport> => {

    // Run agents in parallel (as defined in JSON "Multi-Agent Orchestrator")
    const [creative, media, retention, cro, inventory] = await Promise.all([
        analyzeSegment(
            "Creative Strategy Agent",
            "Focus on ad creative fatigue, UGC opportunities, and angle testing.",
            metrics
        ),
        analyzeSegment(
            "Media Buying Agent",
            "Focus on budget allocation, CBO vs ABO, and scaling winners.",
            metrics
        ),
        analyzeSegment(
            "Retention Marketing Agent",
            "Focus on Klaviyo flows, LTV improvement, and SMS bump.",
            metrics
        ),
        analyzeSegment(
            "CRO Optimization Agent",
            "Focus on landing page speed, checkout friction, and bundle offers.",
            metrics
        ),
        analyzeSegment(
            "Inventory Agent",
            "Focus on stock velocity, dead stock bundles, and cash flow.",
            metrics
        )
    ]);

    const allInsights = [...creative, ...media, ...retention, ...cro, ...inventory];
    const totalOpportunity = allInsights.reduce((sum, item) => sum + (item.revenueImpact || 0), 0);

    // Final Synthesis
    const ai = await getAI();
    const summaryResponse = await ai.models.generateContent({
        model: MODEL_FLASH,
        contents: `Summarize these strategic insights into a cohesive executive summary for the CEO: ${JSON.stringify(allInsights)}`
    });

    return {
        generatedAt: new Date(),
        metrics,
        insights: allInsights,
        totalOpportunity,
        strategySummary: summaryResponse.text || "Analysis complete."
    };
};
