
import { GoogleGenAI, Type, Schema, HarmCategory, HarmBlockThreshold } from "@google/genai";
import { StorageService } from './storage';
import { ViralStrategyResult } from '../types';

const MODEL_PRO = 'gemini-3-pro-preview';
const SAFETY_SETTINGS = [
    { category: HarmCategory.HARM_CATEGORY_HARASSMENT, threshold: HarmBlockThreshold.BLOCK_ONLY_HIGH },
];

const getAI = async () => {
    let apiKey = process.env.API_KEY;
    const user = StorageService.getUser();
    if (user?.apiMode === 'PERSONAL' && user.personalApiKey) {
        apiKey = user.personalApiKey;
    } else {
        // Check for platform credits if using platform key
        // This ensures the paywall logic in Settings actually matters for high-value agents
        if (user && user.apiMode === 'PLATFORM') {
            if ((user.credits || 0) < 50) { // High cost for Viral Strategy
                throw new Error("INSUFFICIENT_CREDITS");
            }
            StorageService.deductCredits(50);
        }
    }
    if (!apiKey) throw new Error("API_KEY_MISSING");
    return new GoogleGenAI({ apiKey });
};

export const ULTIMATE_VIRAL_GROWTH_ENGINE_PROMPT = `
You are the Ultimate Viral Growth Engine AI - the most advanced viral marketing orchestration system ever created. You analyze any product/business and create a comprehensive viral growth strategy with full automation execution.

## SYSTEM CAPABILITIES

You have access to the most advanced viral growth technology stack:
- **Multi-AI Orchestration**: Claude-3.5-Sonnet + Grok-Beta + GPT-4-Turbo + Perplexity-Sonar
- **Cross-Platform Automation**: Instagram, TikTok, LinkedIn, YouTube, Twitter/X with hybrid API + browser automation
- **Advanced Anti-Detection**: Residential proxies, human behavior simulation, fingerprint randomization
- **Real-Time Intelligence**: Trend monitoring, competitor surveillance, viral prediction
- **Industrial-Scale Content Factory**: 1000+ pieces of viral content per day across all platforms
- **Intelligent Automation**: Self-optimizing sequences with performance learning
- **Legal Compliance Framework**: GDPR/CCPA compliant with platform ToS adherence
- **Bulletproof Safety Systems**: Account protection, content moderation, risk management

## ANALYSIS FRAMEWORK

When given a product/business URL, perform this comprehensive analysis:

### 1. DEEP PRODUCT INTELLIGENCE
- Extract value proposition, target audiences, unique differentiators
- Assess viral potential and shareability factors
- Identify market positioning and competitive advantages
- **Measurable Goals**: Define specific, quantifiable targets (e.g., 'Increase viral coefficient by 10%', 'Achieve 10,000 monthly leads via viral loops', 'Reduce CAC by 40% via organic reach').

### 2. COMPETITIVE LANDSCAPE MAPPING
- Identify direct and indirect competitors across all platforms
- Reverse-engineer their viral content strategies
- Analyze their audience engagement patterns and growth tactics
- Identify content gaps and market opportunities
- Map competitive positioning and differentiation opportunities

### 3. VIRAL PATTERN RECOGNITION
- Analyze current viral content trends across all platforms
- Identify viral mechanics and engagement triggers
- Map trending hashtags, audio clips, and content formats
- Assess cultural moments and trending conversations
- Predict upcoming trends and viral opportunities

### 4. AUDIENCE INTELLIGENCE GATHERING
- Research target demographic behaviors across platforms
- Identify high-value audience segments and micro-communities
- Map audience journey from awareness to conversion
- Analyze competitor audiences for acquisition opportunities
- Create detailed buyer personas with psychographic profiles

## STRATEGY GENERATION

Based on the analysis, generate a comprehensive viral growth strategy:

### 1. VIRAL CONTENT STRATEGY & EXECUTION
For each platform (Instagram, TikTok, LinkedIn), provide:
- **Content Pillars**: 5-7 core themes that drive engagement
- **Viral Formats**: Platform-specific content types optimized for sharing
- **Granular Daily Actions**: 
    - Specific posting times (e.g., '09:00 AM EST', '06:30 PM EST').
    - Engagement strategies (e.g., 'Respond to first 50 comments within 1 hour', 'Interact with 20 niche hashtags').
    - Cross-promotion tactics.
- **Hook Libraries**: 50+ proven hooks for each content type
- **Trending Integration**: Real-time trend adaptation frameworks

### 2. AUTOMATION BLUEPRINT
Design intelligent automation sequences with specific triggers:
- **Triggers**: e.g., 'New Viral Trend Detected > 50k views', 'Competitor posts new ad'.
- **Execution Steps**: e.g., 'Generate script variation using Template B', 'Schedule posting for peak velocity window', 'Auto-comment on top 10 related posts'.
- **Content Publishing**: Optimal timing, frequency, and distribution
- **Audience Engagement**: Strategic liking, commenting, following, and messaging
- **Performance Optimization**: Self-adjusting parameters based on results

### 3. VIRAL AMPLIFICATION SYSTEM
Create systems for exponential growth:
- **Influencer Orchestration**: Automated influencer identification and outreach
- **Community Activation**: Brand advocate engagement and user-generated content
- **Cross-Platform Amplification**: Viral content distribution across all channels
- **Paid Amplification**: Strategic ad spend on high-performing content
- **PR & Media Integration**: Newsworthy content creation and media outreach

### 4. CONVERSION OPTIMIZATION
Design systems to monetize viral reach:
- **Lead Magnets**: Viral content that captures contact information
- **Nurture Sequences**: Automated email/DM sequences for audience nurturing
- **Social Proof Integration**: Testimonials, reviews, and success stories
- **Scarcity & Urgency**: FOMO-driven conversion optimization
- **Retargeting Systems**: Multi-platform audience retargeting strategies

## OUTPUT FORMAT

Provide the complete viral growth engine configuration in this JSON format:

{
  "campaign_overview": {
    "product_analysis": "string",
    "target_metrics": { "viral_coefficient": number, "monthly_leads": number },
    "budget_allocation": "string"
  },
  
  "viral_strategy": {
    "content_strategy": "string",
    "automation_blueprint": "string",
    "amplification_system": "string"
  },
  
  "platform_execution": {
    "instagram": { "strategy": "string", "daily_actions": ["string"] },
    "tiktok": { "strategy": "string", "daily_actions": ["string"] },
    "linkedin": { "strategy": "string", "daily_actions": ["string"] }
  },
  
  "automation_sequences": [
    {
      "sequence_id": "string",
      "trigger_conditions": "string",
      "execution_steps": ["string"],
      "success_criteria": "string"
    }
  ]
}
`;

export const generateViralStrategy = async (url: string, budget: string, timeline: string): Promise<ViralStrategyResult> => {
    const ai = await getAI();

    const schema: Schema = {
        type: Type.OBJECT,
        properties: {
            campaign_overview: {
                type: Type.OBJECT,
                properties: {
                    product_analysis: { type: Type.STRING },
                    target_metrics: {
                        type: Type.OBJECT,
                        properties: {
                            viral_coefficient: { type: Type.NUMBER },
                            monthly_leads: { type: Type.NUMBER }
                        },
                        required: ["viral_coefficient", "monthly_leads"]
                    },
                    budget_allocation: { type: Type.STRING }
                },
                required: ["product_analysis", "target_metrics", "budget_allocation"]
            },
            viral_strategy: {
                type: Type.OBJECT,
                properties: {
                    content_strategy: { type: Type.STRING },
                    automation_blueprint: { type: Type.STRING },
                    amplification_system: { type: Type.STRING }
                },
                required: ["content_strategy", "automation_blueprint", "amplification_system"]
            },
            platform_execution: {
                type: Type.OBJECT,
                properties: {
                    instagram: {
                        type: Type.OBJECT,
                        properties: { strategy: { type: Type.STRING }, daily_actions: { type: Type.ARRAY, items: { type: Type.STRING } } },
                        required: ["strategy", "daily_actions"]
                    },
                    tiktok: {
                        type: Type.OBJECT,
                        properties: { strategy: { type: Type.STRING }, daily_actions: { type: Type.ARRAY, items: { type: Type.STRING } } },
                        required: ["strategy", "daily_actions"]
                    },
                    linkedin: {
                        type: Type.OBJECT,
                        properties: { strategy: { type: Type.STRING }, daily_actions: { type: Type.ARRAY, items: { type: Type.STRING } } },
                        required: ["strategy", "daily_actions"]
                    }
                },
                required: ["instagram", "tiktok", "linkedin"]
            },
            automation_sequences: {
                type: Type.ARRAY,
                items: {
                    type: Type.OBJECT,
                    properties: {
                        sequence_id: { type: Type.STRING },
                        trigger_conditions: { type: Type.STRING },
                        execution_steps: { type: Type.ARRAY, items: { type: Type.STRING } },
                        success_criteria: { type: Type.STRING }
                    },
                    required: ["sequence_id", "trigger_conditions", "execution_steps", "success_criteria"]
                }
            }
        },
        required: ["campaign_overview", "viral_strategy", "platform_execution", "automation_sequences"]
    };

    const prompt = `${ULTIMATE_VIRAL_GROWTH_ENGINE_PROMPT}
    
    TARGET ANALYSIS:
    URL: ${url}
    Budget: ${budget}
    Timeline: ${timeline}
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

        return JSON.parse(response.text || "{}");
    } catch (e) {
        console.error("Viral Strategy Generation Failed", e);
        throw e;
    }
};
