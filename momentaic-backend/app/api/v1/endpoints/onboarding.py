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

@router.post("/analyze", response_model=StartupAnalysisResponse)
async def analyze_startup_concept(
    request: StartupAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Analyzes a startup description to infer industry and stage, 
    and generates a context-aware follow-up question.
    """
    from app.agents.base import get_llm
    from langchain_core.messages import SystemMessage, HumanMessage
    import json
    import re

    llm = get_llm("gemini-flash", temperature=0.3)
    
    prompt = f"""Analyze this startup description and infer:
1. The most accurate Industry Category (e.g. FinTech, BioTech, SaaS, E-commerce).
2. The implied Stage (Idea, MVP, Growth, Scale) based on how they describe it.
3. A specific, intelligent follow-up question to clarify their niche or technical approach.

Description: "{request.description}"

Respond in JSON format:
{{
  "industry": "Found Industry",
  "stage": "Inferred Stage",
  "follow_up_question": "Your smart question here?"
}}
"""

    try:
        response = await llm.ainvoke([
            SystemMessage(content="You are an expert VC and Product Analyst. Be precise and concise."),
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
            follow_up_question=data.get("follow_up_question", "Could you elaborate on your core technology?")
        )
        
    except Exception as e:
        # Fallback if AI fails
        return StartupAnalysisResponse(
            industry="Technology",
            stage="idea",
            follow_up_question="Could you tell me more about your target audience?"
        )
