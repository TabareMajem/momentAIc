"""
Trust Architect API Endpoints
Generates enterprise compliance artifacts on demand.
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_active_user, verify_startup_access
from app.models.user import User
from app.models.startup import Startup
from app.agents.trust_architect_agent import trust_architect

router = APIRouter()


# ─── Request Models ───────────────────────────────────

class SOC2Request(BaseModel):
    target_company: str = Field(..., description="Name of the enterprise buyer")

class QuestionnaireRequest(BaseModel):
    questions: List[str] = Field(..., description="List of security questions to answer")

class LOIRequest(BaseModel):
    target_company: str
    scope: str = Field(default="Enterprise License for core platform")
    pricing: str = Field(default="TBD — to be negotiated")
    timeline: str = Field(default="90-day implementation")
    special_conditions: Optional[str] = Field(default=None)


# ─── Response Models ──────────────────────────────────

class TrustArtifactResponse(BaseModel):
    success: bool
    document_type: str
    markdown: Optional[str] = None
    answers: Optional[List[Dict[str, str]]] = None
    generated_at: Optional[str] = None
    error: Optional[str] = None


# ─── Endpoints ────────────────────────────────────────

@router.post("/soc2", response_model=TrustArtifactResponse)
async def generate_soc2_summary(
    startup_id: UUID,
    request: SOC2Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate an enterprise-grade SOC 2 Type II Executive Summary."""
    await verify_startup_access(startup_id, current_user, db)

    startup_result = await db.execute(select(Startup).where(Startup.id == startup_id))
    startup = startup_result.scalar_one_or_none()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")

    result = await trust_architect.generate_soc2_summary(
        startup_context={
            "name": startup.name,
            "description": startup.description,
            "industry": startup.industry,
        },
        target_company=request.target_company,
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Generation failed"))

    return TrustArtifactResponse(**result)


@router.post("/questionnaire", response_model=TrustArtifactResponse)
async def answer_security_questionnaire(
    startup_id: UUID,
    request: QuestionnaireRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Answer a set of enterprise security questions via AI."""
    await verify_startup_access(startup_id, current_user, db)

    startup_result = await db.execute(select(Startup).where(Startup.id == startup_id))
    startup = startup_result.scalar_one_or_none()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")

    result = await trust_architect.answer_security_questionnaire(
        startup_context={
            "name": startup.name,
            "description": startup.description,
        },
        questions=request.questions,
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Generation failed"))

    return TrustArtifactResponse(**result)


@router.post("/loi", response_model=TrustArtifactResponse)
async def draft_loi(
    startup_id: UUID,
    request: LOIRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Draft a non-binding Letter of Intent for an enterprise deal."""
    await verify_startup_access(startup_id, current_user, db)

    startup_result = await db.execute(select(Startup).where(Startup.id == startup_id))
    startup = startup_result.scalar_one_or_none()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")

    result = await trust_architect.draft_loi(
        startup_context={
            "name": startup.name,
            "description": startup.description,
            "industry": startup.industry,
        },
        deal_terms={
            "target_company": request.target_company,
            "scope": request.scope,
            "pricing": request.pricing,
            "timeline": request.timeline,
            "special_conditions": request.special_conditions,
        },
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Generation failed"))

    return TrustArtifactResponse(**result)
