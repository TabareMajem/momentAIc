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
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=settings.google_api_key,
            temperature=temperature,
        )
    elif model.startswith("claude"):
        if not settings.anthropic_api_key:
            logger.warning("Anthropic API key not configured, using mock")
            return None
        return ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            anthropic_api_key=settings.anthropic_api_key,
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
    
    Args:
        query: The search query
    
    Returns:
        Search results as formatted text
    """
    if not settings.serper_api_key:
        return f"[Mock search results for: {query}]\n- Result 1: Sample finding about {query}\n- Result 2: Another insight"
    
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
        
        return "\n".join(results) if results else "No results found"
    except Exception as e:
        logger.error("Web search failed", error=str(e))
        return f"Search failed: {str(e)}"


@tool
def linkedin_search(person_name: str, company: Optional[str] = None) -> str:
    """
    Search LinkedIn for a person's profile information.
    
    Args:
        person_name: Name of the person to search
        company: Optional company name to refine search
    
    Returns:
        LinkedIn profile information
    """
    # In production, integrate with LinkedIn API or use Proxycurl
    query = f"{person_name} {company or ''} site:linkedin.com"
    return f"[LinkedIn data for {person_name}]\n- Title: CEO at {company or 'Unknown'}\n- Recent activity: Posted about AI trends"


@tool
def company_research(company_name: str) -> str:
    """
    Research a company to find relevant information.
    
    Args:
        company_name: Name of the company to research
    
    Returns:
        Company information
    """
    return f"[Company Research: {company_name}]\n- Industry: Technology\n- Size: 50-200 employees\n- Recent news: Series A funding announced"


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
        "sentiment": "positive",
        "confidence": 0.85,
        "key_phrases": ["innovative", "excited", "opportunity"]
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
    return [
        f"AI in {industry}",
        f"Future of {industry}",
        f"{industry} automation trends",
        "Startup funding news",
        "Remote work evolution"
    ]


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
}


def get_agent_config(agent_type: AgentType) -> Dict[str, Any]:
    """Get configuration for an agent type"""
    return AGENT_CONFIGS.get(agent_type, AGENT_CONFIGS[AgentType.GENERAL])
