from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.agents.growth_hacker_agent import growth_hacker_agent
from app.agents.marketing_agent import marketing_agent

router = APIRouter()

class WizardRequest(BaseModel):
    url: str
    description: Optional[str] = ""

class WizardResponse(BaseModel):
    strategy: Dict[str, Any]
    generated_post: str

@router.post("/wizard", response_model=WizardResponse)
async def run_onboarding_wizard(
    request: WizardRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    60-Second Result: Auto-generates a growth strategy and first viral post.
    """
    # 1. Analyze Startup
    strategy = await growth_hacker_agent.analyze_startup_wizard(
        url=request.url,
        description=request.description
    )
    
    if "error" in strategy:
        raise HTTPException(status_code=500, detail=strategy["error"])
        
    # 2. Draft First Post (using Marketing Agent + Feedback Loop Logic implicitly via draft)
    # We can use the viral_post_hook from strategy to seed the post
    hook = strategy.get("viral_post_hook", "")
    audience = strategy.get("target_audience", "")
    
    # Generate a quick draft based on the hook
    if hook:
        draft = await marketing_agent.create_social_post(
            context=f"Target Audience: {audience}. Hook: {hook}. Goal: Viral Launch.",
            platform="linkedin_x"
        )
    else:
        draft = "Check out our new launch!"
        
    return {
        "strategy": strategy,
        "generated_post": draft
    }
    return {
        "strategy": strategy,
        "generated_post": draft
    }


class StartupAnalysisRequest(BaseModel):
    description: str

class StartupAnalysisResponse(BaseModel):
    industry: str
    stage: str
    follow_up_question: str
    summary: str
    potential_competitors: List[str]
    insight: str

@router.post("/analyze", response_model=StartupAnalysisResponse)
async def analyze_startup_concept(
    request: StartupAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Analyzes a startup description using a heavy-lifting prompt to provide
    strategic insights, infer industry/stage, and prove understanding.
    """
    from app.agents.base import get_llm
    from langchain_core.messages import SystemMessage, HumanMessage
    import json
    import re

    # Use DeepSeek V3 for "WOW" reasoning at low cost
    llm = get_llm("deepseek-chat", temperature=0.6)
    
    prompt = f"""You are a world-class Venture Capitalist and Product Strategist (like Paul Graham meets refined AI).
    
    Your goal is to analyze a raw startup idea/description and provide an "Immediate Insight" that WOWs the founder.
    The founder thinks most advice is generic. PROVE THEM WRONG.
    
    Input Description: "{request.description}"
    
    Task:
    1.  **Summarize & Validate**: In 1 sentence, rephrase what they are building to prove you understand it (e.g., "You're building an Airbnb for X...").
    2.  **Identify Industry**: Be specific. Not just "SaaS", but "Vertical SaaS for HVAC" or "Generative AI for Legal".
    3.  **Infer Stage**: (Idea, Prototype, MVP, Growth, Scale) based on the nuance of their text.
    4.  **Strategic Insight**: Give one high-value, non-obvious observation. It could be a risk, a distribution channel to try, or a core metric to focus on. BE SPECIFIC.
    5.  **Competitors**: Name 2-3 real or likely competitors/analogous companies.
    6.  **Follow-up Question**: Ask the ONE most critical question that would determine if this business lives or dies.
    
    Return pure JSON:
    {{
      "industry": "...",
      "stage": "...",
      "summary": "...",
      "insight": "...",
      "potential_competitors": ["Comp1", "Comp2"],
      "follow_up_question": "..."
    }}
    """

    try:
        response = await llm.ainvoke([
            SystemMessage(content="You are an expert VC. Be sharp, concise, and insightful. Output JSON only."),
            HumanMessage(content=prompt)
        ])
        
        content = response.content
        # Clean markdown checks
        content = re.sub(r"```json\s*", "", content)
        content = re.sub(r"```\s*", "", content)
        
        data = json.loads(content)
        
        return StartupAnalysisResponse(
            industry=data.get("industry", "Technology"),
            stage=data.get("stage", "idea"),
            summary=data.get("summary", "An innovative tech project."),
            insight=data.get("insight", "Focus on validating your core value proposition first."),
            potential_competitors=data.get("potential_competitors", []),
            follow_up_question=data.get("follow_up_question", "What is your go-to-market strategy?")
        )
        
    except Exception as e:
        # Fallback if AI fails
        return StartupAnalysisResponse(
            industry="Technology",
            stage="idea",
            summary="A new technology startup.",
            insight="Ensure you have a clear target audience.",
            potential_competitors=[],
            follow_up_question="Could you tell me more about your target audience?"
        )
