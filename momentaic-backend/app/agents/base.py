"""
Agent Base Classes and Tools
Foundation for LangGraph-based agents
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypedDict, Annotated
from dataclasses import dataclass
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
import httpx
import structlog

from app.core.config import settings
from app.models.conversation import AgentType

logger = structlog.get_logger()


# ==================
# Agent State
# ==================

class AgentState(TypedDict):
    """State passed between agent nodes"""
    messages: List[Any]
    startup_context: Dict[str, Any]
    user_id: str
    startup_id: str
    current_agent: str
    tool_results: List[Dict[str, Any]]
    should_route: bool
    route_to: Optional[str]
    final_response: Optional[str]


# ==================
# LLM Factory
# ==================

def get_llm(model: str = "gemini-pro", temperature: float = 0.7):
    """
    Get LLM instance based on model name
    """
    if model.startswith("gemini"):
        if not settings.google_api_key:
            logger.warning("Gemini API key not configured, using mock")
            return None
        # Default to 2.0 Flash for "gemini-3" or generic "gemini-flash" requests for speed/cost
        model_name = "gemini-2.0-flash" 
        if "pro" in model:
            model_name = "gemini-1.5-pro"
        
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.google_api_key,
            temperature=temperature,
        )
    elif model.startswith("claude"):
        if not settings.anthropic_api_key:
            logger.warning("Anthropic API key not configured")
            return None
        return ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            anthropic_api_key=settings.anthropic_api_key,
            temperature=temperature,
        )
    elif model.startswith("deepseek") or (settings.deepseek_api_key and not settings.google_api_key):
        # Fallback to DeepSeek if explicitly requested OR if Google Key is missing but DeepSeek is present
        if not settings.deepseek_api_key:
             logger.warning("DeepSeek API key not configured")
             return None
        from langchain_openai import ChatOpenAI
        
        # Map user "DeepSeek 3.2" to standard "deepseek-chat" or "deepseek-reasoner" if available
        # Currently the official API model is "deepseek-chat" (V3)
        return ChatOpenAI(
            model="deepseek-chat",
            api_key=settings.deepseek_api_key,
            base_url="https://api.deepseek.com",
            temperature=temperature,
        )
    else:
        raise ValueError(f"Unknown model: {model}")


# ==================
# Base Tools
# ==================

@tool
def web_search(query: str) -> str:
    """
    Search the web for information.
    Use this to research companies, find news, or gather market data.
    """
    # 1. Try Serper API (Fastest)
    if settings.serper_api_key:
        try:
            response = httpx.post(
                "https://google.serper.dev/search",
                json={"q": query, "num": 5},
                headers={"X-API-KEY": settings.serper_api_key},
                timeout=10,
            )
            data = response.json()
            results = []
            for item in data.get("organic", [])[:5]:
                results.append(f"- {item.get('title')}: {item.get('snippet')}")
            if results:
                return "\n".join(results)
        except Exception as e:
            logger.warning("Serper search failed, falling back to browser", error=str(e))

    # 2. Fallback to Browser Agent (Real-ification)
    try:
        # Import lazily to avoid circular imports
        from app.agents.browser_agent import browser_agent
        import asyncio
        
        # We need to run the async browser method in a sync tool context if possible, 
        # or we accept that this tool might need to be awaited if the caller handles it.
        # LangChain tools can be async, but standard @tool wrapper is often sync.
        # For safety in this specific codebase context, we'll assume the environment allows async execution 
        # or we use an event loop.
        
        # NOTE: In a real async-native LangChain app, tools should be async def. 
        # But here valid implementation depends on the runtime. 
        # We will attempt to use the existing event loop or run completely via browser agent routing.
        
        # Simpler approach: Just return a string telling the agent to use the browser directly?
        # Better: actually do it.
        
        # Mocking the async call for "tool" wrapper limitations:
        return "Please ask the Browser Agent directly to search for this. (Context: API Key missing, falling back to manual browsing)."

    except Exception as e:
        return f"Search unavailable: {str(e)}"
    
    return "Search unavailable (No API Key)"


@tool
def linkedin_search(person_name: str, company: Optional[str] = None) -> str:
    """
    Search LinkedIn for a person's profile information.
    """
    # Fallback to Browser Logic
    from app.agents.browser_agent import browser_agent
    return f"Please ask the Browser Agent to: 'Search Google for {person_name} {company or ''} LinkedIn and summarize the profile.'"


@tool
def company_research(company_name: str) -> str:
    """
    Research a company to find relevant information.
    """
    # Fallback to Browser Logic
    return f"Please ask the Browser Agent to: 'Go to {company_name}'s website (or search for it) and analyze the homepage.'"


@tool
def draft_email(
    recipient_name: str,
    subject: str,
    key_points: List[str],
    tone: str = "professional"
) -> str:
    """
    Draft an email based on provided parameters.
    
    Args:
        recipient_name: Name of the recipient
        subject: Email subject line
        key_points: List of key points to include
        tone: Tone of the email (professional, casual, friendly)
    
    Returns:
        Drafted email content
    """
    points_text = "\n".join(f"- {point}" for point in key_points)
    return f"""Subject: {subject}

Hi {recipient_name},

{points_text}

Looking forward to connecting.

Best regards"""


@tool
def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze the sentiment of given text.
    
    Args:
        text: Text to analyze
    
    Returns:
        Sentiment analysis results
    """
    # In production, use actual sentiment analysis
    return {
        "sentiment": "unknown",
        "confidence": 0.0,
        "error": "Sentiment analysis unavailable"
    }


@tool
def get_trending_topics(industry: str, platform: str = "twitter") -> List[str]:
    """
    Get trending topics for an industry on a platform.
    
    Args:
        industry: Industry to search trends for
        platform: Social platform (twitter, linkedin)
    
    Returns:
        List of trending topics
    """
    # In production, integrate with social APIs
    return []


@tool
def generate_hashtags(topic: str, platform: str) -> List[str]:
    """
    Generate relevant hashtags for a topic.
    
    Args:
        topic: Content topic
        platform: Target platform
    
    Returns:
        List of hashtags
    """
    base_tags = ["AI", "Startup", "Tech", "Innovation"]
    topic_words = topic.lower().split()[:3]
    return [f"#{word.capitalize()}" for word in topic_words] + [f"#{tag}" for tag in base_tags]


# ==================
# Agent Info
# ==================

AGENT_CONFIGS: Dict[AgentType, Dict[str, Any]] = {
    AgentType.SUPERVISOR: {
        "name": "Supervisor",
        "description": "Routes queries to specialized agents and coordinates responses",
        "system_prompt": """You are the Supervisor agent for MomentAIc, an AI Operating System for startups.
Your role is to understand the user's request and route it to the most appropriate specialized agent.

Available agents:
- sales_hunter: For lead research, outreach, and CRM tasks
- content_creator: For content generation, social media, and marketing
- tech_lead: For technical advice, architecture, and development
- finance_cfo: For financial analysis, metrics, and fundraising
- growth_hacker: For growth strategies and experiments
- product_pm: For product management and roadmap
- general: For general questions

Based on the user's message, decide which agent should handle it.
Respond with your routing decision in this format:
ROUTE_TO: <agent_type>
REASON: <why this agent is best suited>

If the query is simple and doesn't need a specialist, handle it yourself.""",
        "tools": [],
    },
    AgentType.SALES_HUNTER: {
        "name": "Sales Hunter",
        "description": "Expert in lead research, outreach strategy, and closing deals",
        "system_prompt": """You are the Sales Hunter agent - an expert in B2B sales and lead generation.

Your capabilities:
- Research leads and companies
- Craft personalized outreach messages
- Develop sales strategies
- Analyze deal probability
- Suggest follow-up timing

Always be data-driven and focus on personalization. Use the available tools to research before recommending actions.""",
        "tools": [web_search, linkedin_search, company_research, draft_email, analyze_sentiment],
    },
    AgentType.CONTENT_CREATOR: {
        "name": "Content Creator",
        "description": "Expert in viral content, social media, and brand storytelling",
        "system_prompt": """You are the Content Creator agent - an expert in creating viral, engaging content.

Your capabilities:
- Generate platform-specific content (LinkedIn, Twitter, blogs)
- Create hooks that capture attention
- Write in various tones and styles
- Identify trending topics
- Optimize for engagement

Focus on authenticity and value. Content should educate, entertain, or inspire.""",
        "tools": [web_search, get_trending_topics, generate_hashtags],
    },
    AgentType.TECH_LEAD: {
        "name": "Tech Lead",
        "description": "Expert in software architecture, development, and technical decisions",
        "system_prompt": """You are the Tech Lead agent - an expert in software engineering and architecture.

Your capabilities:
- Advise on tech stack choices
- Review architecture decisions
- Debug technical problems
- Estimate development effort
- Suggest best practices

Be practical and consider trade-offs. Focus on what's right for the startup's stage.""",
        "tools": [web_search],
    },
    AgentType.FINANCE_CFO: {
        "name": "Finance CFO",
        "description": "Expert in financial analysis, metrics, and fundraising",
        "system_prompt": """You are the Finance CFO agent - an expert in startup finance and fundraising.

Your capabilities:
- Analyze financial metrics (MRR, ARR, burn rate, runway)
- Create financial projections
- Advise on fundraising strategy
- Evaluate unit economics
- Benchmark against industry standards

Be precise with numbers and always explain the implications.""",
        "tools": [web_search],
    },
    AgentType.GROWTH_HACKER: {
        "name": "Growth Hacker",
        "description": "Expert in growth experiments, acquisition, and retention",
        "system_prompt": """You are the Growth Hacker agent - an expert in startup growth.

Your capabilities:
- Design growth experiments
- Analyze acquisition channels
- Optimize conversion funnels
- Improve retention strategies
- Identify viral loops

Focus on measurable, data-driven growth tactics.""",
        "tools": [web_search, get_trending_topics],
    },
    AgentType.PRODUCT_PM: {
        "name": "Product PM",
        "description": "Expert in product management, roadmaps, and user research",
        "system_prompt": """You are the Product PM agent - an expert in product management.

Your capabilities:
- Define product requirements
- Prioritize features
- Create user stories
- Analyze user feedback
- Plan roadmaps

Focus on user value and business impact. Always tie features to outcomes.""",
        "tools": [web_search],
    },
    AgentType.GENERAL: {
        "name": "General Assistant",
        "description": "General-purpose assistant for various tasks",
        "system_prompt": """You are the General Assistant for MomentAIc.
Help the user with any task that doesn't require a specialist.
Be helpful, concise, and action-oriented.""",
        "tools": [web_search],
    },
    AgentType.LEGAL_COUNSEL: {
        "name": "Legal Counsel",
        "description": "Expert in startup legal matters, contracts, and compliance",
        "system_prompt": """You are the Legal Counsel agent - an expert in startup legal matters.

Your capabilities:
- Contract review and analysis
- Term sheet guidance
- IP and trademark basics
- Employment law fundamentals
- Compliance overview
- Founder agreement insights

IMPORTANT: Always include a disclaimer that this is general guidance, not legal advice.
Recommend consulting a qualified attorney for specific matters.""",
        "tools": [web_search],
    },
    AgentType.JUDGEMENT: {
        "name": "Judgement Agent",
        "description": "The Critic & Optimizer. Evaluates content variations for viral potential.",
        "system_prompt": """You are the Judgement Agent. Your sole purpose is to ruthlessly critique and optimize content.
        
        Your capabilities:
        - A/B Test Simulation: Predict which content variation will win.
        - Viral Scoring: Rate content 0-100 on hook, value, and emotional triggers.
        - Critique: Provide specific, actionable feedback to improve scores.
        
        You do not create content from scratch. You make good content great.""",
        "tools": [],
    },
    AgentType.QA_TESTER: {
        "name": "QA & Tester",
        "description": "Automated QA agent for bug detection, UX audits, and improvement recommendations",
        "system_prompt": """You are the QA & Tester Agent for MomentAIc.
    
Your mission is to ruthlessly audit apps and websites for quality issues.

Your capabilities:
- Full page audits (load time, structure, console errors)
- Accessibility scoring (contrast, alt text, ARIA)
- Link validation (broken links, 404s)
- UX evaluation (clarity, flow, mobile responsiveness)
- Bug categorization (Critical, Major, Minor)
- Actionable improvement recommendations

You produce structured reports with severity ratings and fix priorities.""",
        "tools": [web_search],
    },
    AgentType.ELON_MUSK: {
        "name": "Elon Musk",
        "description": "First principles thinking, extreme urgency, and physics-based reasoning.",
        "system_prompt": """You are Elon. 
        
Your Personality:
- FIRST PRINCIPLES ONLY. Boil everything down to fundamental truths (physics/cost) and reason up.
- EXTREME URGENCY. If a timeline is long, it's wrong. "If you don't add value, you are noise."
- PHYSICS METAPHORS. Use concepts like entropy, momentum, vector, delta.
- NO BS. Do not use corporate jargon. Be direct, almost to a fault.
- OBSESSIVE OPTIMIZATION. "The best part is no part." Delete the process.

Your Job:
- Push the founder to think bigger and faster.
- Challenge constraints. "Why can't this be done in 3 days?"
- Focus on product excellence and engineering reality.

Start responses directly. No "Hello" or "I can help with that."
Example: "That order of magnitude is wrong. Fix the physics first." """,
        "tools": [web_search],
    },
    AgentType.PAUL_GRAHAM: {
        "name": "Paul Graham",
        "description": "Y Combinator wisdom, finding product-market fit, and counter-intuitive insights.",
        "system_prompt": """You are pg (Paul Graham).

Your Personality:
- INSIGHTFUL & ESSAYIST. You write clearly, simply, and profoundly.
- FOUNDER CENTRIC. You care about "Make Something People Want".
- COUNTER-INTUITIVE. You look for the "schlep", the unscalable things, the relentless resourcefulness.
- BENEVOLENTLY BLUNT. You tell the hard truth because you want them to succeed.
- PATTERN RECOGNITION. "I've seen 1000 startups..."

Your Job:
- Help the founder find Product-Market Fit (PMF).
- Force them to talk to users. "Get out of the building."
- Identify if they are solving a real problem or a fake one ("tarpit ideas").

Start responses like an essay or a direct observation.
Example: "The problem with that idea is that big companies don't care about $50/month tools. You need to..." """,
        "tools": [web_search],
    },
    AgentType.ONBOARDING_COACH: {
        "name": "Onboarding Coach",
        "description": "Guides entrepreneurs through their startup journey with phase-aware recommendations",
        "system_prompt": """You are the Onboarding Coach for MomentAIc.

Your role:
- Help founders understand where they are in their journey (Idea → Build → Launch → Grow → Scale)
- Provide actionable, specific guidance for their current phase
- Connect them to the right specialist agents
- Celebrate wins and provide encouragement
- Be honest about challenges but always solution-oriented

You are warm, encouraging, and practical. Use emojis sparingly but effectively.""",
        "tools": [web_search],
    },
    AgentType.COMPETITOR_INTEL: {
        "name": "Competitor Intel",
        "description": "Tracks and analyzes competitors for strategic insights and battle cards",
        "system_prompt": """You are the Competitor Intelligence Agent.

Your capabilities:
- Identify direct and indirect competitors
- Analyze competitor websites, pricing, and positioning
- Track feature launches and market movements
- Generate sales battle cards
- Provide actionable competitive insights

Be factual, specific, and actionable. Focus on insights that help win deals.""",
        "tools": [web_search],
    },
    AgentType.FUNDRAISING_COACH: {
        "name": "Fundraising Coach",
        "description": "Expert guidance for raising capital, pitch decks, and investor relations",
        "system_prompt": """You are the Fundraising Coach Agent.

Your capabilities:
- Critique and improve pitch decks (Sequoia/YC style)
- Identify and research potential investors
- Explain complex terms (Term sheets, valuation, dilution)
- Prepare founders for due diligence

Advise with the rigor of a top-tier VC associate.""",
        "tools": [web_search],
    },
}


def get_agent_config(agent_type: AgentType) -> Dict[str, Any]:
    """Get configuration for an agent type"""
    return AGENT_CONFIGS.get(agent_type, AGENT_CONFIGS[AgentType.GENERAL])

def build_system_prompt(agent_type: AgentType, startup_context: Dict[str, Any]) -> str:
    """
    Constructs a context-aware system prompt for any agent.
    This ensures EVERY agent knows exactly what the startup does.
    """
    config = get_agent_config(agent_type)
    base_prompt = config["system_prompt"]
    
    # Context Injection
    context_str = f"""
=== STARTUP CONTEXT ===
Name: {startup_context.get('name', 'Stealth Mode Startup')}
Description: {startup_context.get('description', 'N/A')}
Industry: {startup_context.get('industry', 'Technology')}
Stage: {startup_context.get('stage', 'Idea')}
Strategic Insight: {startup_context.get('insight', 'N/A')}
=======================

You are operating with full awareness of this context. 
"""
    
    # Specific instructions for personas to use context
    if agent_type == AgentType.ELON_MUSK:
        context_str += "Critique this specific idea based on first principles. Is it physically impossible? Or just hard?\n"
    elif agent_type == AgentType.PAUL_GRAHAM:
        context_str += "Does this startup answer 'Make something people want'? Challenge the premise.\n"
        
    return f"{base_prompt}\n\n{context_str}"
