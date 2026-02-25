"""
Agent Base Classes and Tools
Foundation for LangGraph-based agents
"""

from abc import ABC, abstractmethod
import json
import re
from typing import Any, Dict, List, Optional, TypedDict, Annotated, TypeVar, Type
from pydantic import BaseModel, ValidationError
from dataclasses import dataclass
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
import httpx
import structlog

from app.core.config import settings
from app.models.conversation import AgentType
from app.services.activity_stream import activity_stream

logger = structlog.get_logger()

T = TypeVar("T", bound=BaseModel)

def safe_parse_json(response_text: str) -> Dict[str, Any]:
    """Robustly extract JSON from an LLM response."""
    try:
         return json.loads(response_text)
    except json.JSONDecodeError:
         pass
         
    # Extract markdown json block
    if "```json" in response_text:
         content = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
         content = response_text.split("```")[1].split("```")[0].strip()
    else:
         content = response_text
         
    try:
         return json.loads(content)
    except json.JSONDecodeError:
         pass
         
    # Ultimate fallback regex hack
    match = re.search(r'\{[\s\S]*\}', content)
    if match:
         try:
             return json.loads(match.group(0))
         except json.JSONDecodeError:
             pass
             
    # Try array fallback
    arr_match = re.search(r'\[[\s\S]*\]', content)
    if arr_match:
         try:
             return json.loads(arr_match.group(0))
         except json.JSONDecodeError:
             pass
             
    return {} # Return empty struct if all fails


class BaseAgent(ABC):
    """
    Base Agent class that cognitive agents should inherit from.
    Provides structured output mapping and common utilities.
    """
    
    async def structured_llm_call(
        self, 
        prompt: str, 
        response_model: Type[T] = None,
        model_name: str = "gemini-flash",
        temperature: float = 0.7
    ) -> Any:
        """
        Make a call to the LLM and guarantee structured output.
        If response_model is provided, returns Pydantic object.
        Otherwise returns a parsed Dict.
        """
        llm = get_llm(model_name, temperature=temperature)
        if response_model and hasattr(llm, "with_structured_output"):
             structured_llm = llm.with_structured_output(response_model)
             return await structured_llm.ainvoke(prompt)
             
        response = await llm.ainvoke(prompt)
        parsed_dict = safe_parse_json(response.content)
        
        if response_model:
             try:
                  return response_model.model_validate(parsed_dict)
             except ValidationError as e:
                  logger.error("Structured LLM call failed validation", error=str(e), data=parsed_dict)
                  # If we failed to validate, just return raw dictionary as fallback
                  return parsed_dict
        return parsed_dict

    async def self_correcting_call(
        self,
        prompt: str,
        goal: str = "High quality response",
        target_audience: str = "General",
        response_model: Type[T] = None,
        model_name: str = "gemini-pro",
        temperature: float = 0.7,
        max_iterations: int = 3,
        threshold: int = 85
    ) -> Any:
        """
        Generalized 'Draft -> Critique -> Rewrite' loop utilizing JudgementAgent.
        """
        # 1. Initial Draft
        draft_response = await self.structured_llm_call(
            prompt=prompt,
            response_model=response_model,
            model_name=model_name,
            temperature=temperature
        )
        
        # We need a string representation to critique
        if isinstance(draft_response, BaseModel):
            draft_str = draft_response.model_dump_json()
        elif isinstance(draft_response, dict):
            draft_str = json.dumps(draft_response)
        else:
            draft_str = str(draft_response)

        from app.agents.judgement_agent import judgement_agent
        
        current_draft = draft_response
        current_draft_str = draft_str
        
        for iteration in range(max_iterations):
            # Evaluate current draft
            evaluation = await judgement_agent.evaluate_content(
                goal=goal,
                target_audience=target_audience,
                variations=[current_draft_str]
            )
            
            if "error" in evaluation:
                logger.warning(f"Self-correction loop evaluation failed: {evaluation['error']}")
                return current_draft
                
            scores = evaluation.get("scores", [0])
            score = scores[0] if scores else 0
            
            # If good enough, break
            if score >= threshold:
                break
                
            critiques = evaluation.get("critique", [])
            critique_text = "\\n".join(critiques)
            
            # 2. Rewrite based on critique
            rewrite_prompt = f"""
            {prompt}
            
            === PREVIOUS ATTEMPT ===
            {current_draft_str}
            
            === CRITIQUE FROM EXPERT REVIEWER ===
            Your previous attempt scored {score}/100.
            Here is the critical feedback to improve it:
            {critique_text}
            
            Please REWRITE the response to specifically address this feedback and achieve a score > {threshold}.
            """
            
            current_draft = await self.structured_llm_call(
                prompt=rewrite_prompt,
                response_model=response_model,
                model_name=model_name,
                temperature=temperature
            )
            
            if isinstance(current_draft, BaseModel):
                current_draft_str = current_draft.model_dump_json()
            elif isinstance(current_draft, dict):
                current_draft_str = json.dumps(current_draft)
            else:
                current_draft_str = str(current_draft)
                
        return current_draft

    async def handle_message(self, msg: Any) -> None:
        """
        Default A2A Message Bus handler.
        Override in subclasses for specific routing behavior.
        """
        logger.info(f"Agent {self.__class__.__name__} received unhandled message {msg.id}: {msg.topic}")
        pass



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
    # ... (rest of get_llm as before, omitted for brevity, logic remains in function)
    # Wait, replace_file_content replaces the whole block. I need to be careful not to delete get_llm.
    # Actually, BaseAgent is a module, not a class in this file. It seems this file contains tools and configurations.
    # The actual Agent classes inherit from something? Or are they standalone functions?
    # Let's check ContentAgent again. It inherits nothing explicit in the outline? 
    # Ah, I see from `marketing_agent.py` outline: `class MarketingAgent:`. And `content_agent.py`: `class ContentAgent:`.
    # It seems they don't inherit from a common `BaseAgent` class defined HERE.
    # This `base.py` module contains shared tools and `get_llm`.
    
    # I should check if there IS a BaseAgent class.
    # The file content shows `class AgentState(TypedDict):`.
    # It does NOT show a `class BaseAgent:`.
    
    # So I cannot add methods to a BaseAgent class here.
    # I should instead add a mixin or just import `activity_stream` in each agent.
    # OR, better: Add a `BaseAgent` class here and have agents inherit from it.
    # BUT that requires refactoring all agents.
    
    # Alternative: Create a helper function `report_agent_progress` in this file that agents can import.
    pass

# Retrying with correct approach:
# I will add a helper function `run_proactive_wrapper` or similar, OR just let agents import `activity_stream` directly.
# The plan said "Add report_progress() to base agent". 
# If there is no BaseAgent class, I should probably create one or just use the service directly.
# Let's just use the service directly in `main.py` scheduler logic for now to report status,
# and modify the agents to report progress if I can.
# Given I cannot easily refactor 42 agents to inherit from a new class right now without risk,
# I will modifying `main.py` to handle the reporting wrapper.

# Wait, `ContentAgent` and others seem to be standalondef get_llm(model: str = "gemini-2.5-pro", temperature: float = 0.7):
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
            model_name = "gemini-2.5-pro"
        
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
    elif model.startswith("gpt") or model.startswith("openai"):
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not configured")
            return None
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model if model.startswith("gpt") else "gpt-4-turbo",
            api_key=settings.openai_api_key,
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
async def web_search(query: str) -> str:
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
        
        logger.info(f"Using BrowserAgent to fallback search for: {query}")
        
        # Use simple Google search via browser automation
        search_results = await browser_agent.search_google(query)
        
        results = []
        for item in search_results:
            title = item.get('title', 'No Title')
            snippet = item.get('snippet', '')
            link = item.get('link', '')
            results.append(f"- {title} ({link}): {snippet}")
            
        if results:
            return "\n".join(results)
        else:
            return "No results found via browser search."

    except Exception as e:
        logger.error("Browser search failed", error=str(e))
        return f"Search unavailable: {str(e)}"


@tool
async def linkedin_search(person_name: str, company: Optional[str] = None) -> str:
    """
    Search LinkedIn for a person's profile information.
    """
    try:
        from app.agents.browser_agent import browser_agent
        
        query = f"site:linkedin.com/in/ {person_name} {company or ''}".strip()
        logger.info(f"Using BrowserAgent to searching LinkedIn for: {query}")
        
        search_results = await browser_agent.search_google(query)
        
        results = []
        for item in search_results:
            title = item.get('title', 'No Title')
            snippet = item.get('snippet', '')
            link = item.get('link', '')
            results.append(f"- {title} ({link}): {snippet}")
            
        if results:
            return "\n".join(results)
        else:
            return "No LinkedIn profiles found via browser search."
            
    except Exception as e:
        logger.error("LinkedIn search failed", error=str(e))
        return f"Search unavailable: {str(e)}"


@tool
async def company_research(company_name: str) -> str:
    """
    Research a company to find relevant information.
    """
    try:
        from app.agents.browser_agent import browser_agent
        
        logger.info(f"Using BrowserAgent to research company: {company_name}")
        
        # 1. Search for the company site
        query = f"{company_name} official website and news"
        search_results = await browser_agent.search_google(query)
        
        if not search_results:
             return "Company not found via search."
             
        # Format search results
        search_summary = "\n".join([f"- {r.get('title')}: {r.get('snippet')}" for r in search_results[:3]])
        
        # 2. Try to visit the top link if it looks official (skip social media)
        top_link = search_results[0].get("link")
        site_content = ""
        
        if top_link and "linkedin" not in top_link and "facebook" not in top_link:
             logger.info(f"Navigating to potential company site: {top_link}")
             browse_result = await browser_agent.navigate(top_link)
             if browse_result.success:
                 site_summary = browse_result.text_content[:1000] # First 1000 chars
                 site_content = f"\n\nWebsite Content Summary ({top_link}):\n{site_summary}..."
        
        return f"Search Results:\n{search_summary}{site_content}"

    except Exception as e:
        logger.error("Company research failed", error=str(e))
        return f"Research unavailable: {str(e)}"

@tool
async def read_url_content(url: str) -> str:
    """
    Read the full text content of a specific URL.
    Useful for deep research, summarizing articles, or analyzing competitor pages.
    """
    try:
        from app.agents.browser_agent import browser_agent
        
        # Initialize browser if needed (it is lazy)
        await browser_agent.initialize()
        
        logger.info(f"Reading URL: {url}")
        result = await browser_agent.navigate(url)
        
        if result.success and result.text_content:
            return f"Source: {url}\nTitle: {result.title}\n\nContent:\n{result.text_content[:20000]}" # Increase limit for deep research
        else:
            return f"Failed to read content from {url}. Error: {result.error}"

    except Exception as e:
        logger.error("Read URL failed", url=url, error=str(e))
        return f"Error reading URL: {str(e)}"


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
async def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    [PHASE 25 FIX] Real sentiment analysis using Gemini Flash.
    
    Args:
        text: Text to analyze
    
    Returns:
        Sentiment analysis results
    """
    try:
        llm = get_llm("gemini-flash")
        response = await llm.ainvoke(
            f"Analyze the sentiment of this text. Return strictly JSON with keys: sentiment (positive/negative/neutral), confidence (0.0-1.0), and score (-1.0 to 1.0). Text: {text[:500]}"
        )
        return safe_parse_json(response.content)
    except Exception as e:
        return {"sentiment": "neutral", "confidence": 0.5, "error": str(e)}


@tool
async def get_trending_topics(industry: str, platform: str = "twitter") -> List[str]:
    """
    [PHASE 25 FIX] Get trending topics using AI knowledge/browsing.
    
    Args:
        industry: Industry to search trends for
        platform: Social platform
    
    Returns:
        List of trending topics
    """
    try:
        llm = get_llm("gemini-flash")
        response = await llm.ainvoke(
            f"List 5 currently trending topics or news themes for the '{industry}' industry on {platform}. Return strictly a JSON list of strings, e.g. [\"Topic A\", \"Topic B\"]."
        )
        return safe_parse_json(response.content)
    except Exception as e:
        return [f"{industry} Trends", "Innovation", "Growth"]


@tool
async def generate_hashtags(topic: str, platform: str) -> List[str]:
    """
    [PHASE 25 FIX] Generate relevant hashtags using AI.
    
    Args:
        topic: Content topic
        platform: Target platform
    
    Returns:
        List of hashtags
    """
    try:
        llm = get_llm("gemini-flash")
        response = await llm.ainvoke(
            f"Generate 5 relevant, high-visibility hashtags for the topic '{topic}' on {platform}. Return strictly a JSON list of strings including the # symbol."
        )
        return safe_parse_json(response.content)
    except Exception as e:
        return ["#Innovation", "#Tech", "#Growth"]
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
    locale = startup_context.get('locale', 'en')
    context_str = f"""
=== STARTUP CONTEXT ===
Name: {startup_context.get('name', 'Stealth Mode Startup')}
Description: {startup_context.get('description', 'N/A')}
Industry: {startup_context.get('industry', 'Technology')}
Stage: {startup_context.get('stage', 'Idea')}
Strategic Insight: {startup_context.get('insight', 'N/A')}
Target Localization Code: {locale}
=======================

You are operating with full awareness of this context. 
CRITICAL DIRECTIVE: You ABSOLUTELY MUST communicate, format, and generate all output entirely in the language corresponding to the Target Localization Code ({locale}).
"""
    
    # Specific instructions for personas to use context
    if agent_type == AgentType.ELON_MUSK:
        context_str += "Critique this specific idea based on first principles. Is it physically impossible? Or just hard?\n"
    elif agent_type == AgentType.PAUL_GRAHAM:
        context_str += "Does this startup answer 'Make something people want'? Challenge the premise.\n"
        
    return f"{base_prompt}\n\n{context_str}"
