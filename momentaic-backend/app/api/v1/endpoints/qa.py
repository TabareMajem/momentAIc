"""
QA API Endpoints
Automated app auditing and testing with credit-gated personality modes
"""

from typing import Optional, Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user, require_credits
from app.core.database import get_db
from app.models.user import User
from app.agents.qa_tester_agent import qa_tester_agent

router = APIRouter(prefix="/qa", tags=["QA & Testing"])


# ==================
# Credit Costs
# ==================
CREDIT_COSTS = {
    "basic": 5,       # Basic audit: console errors, broken links, load time
    "full": 15,       # Full QA + UX Review + AI analysis
    "roast": 25,      # Brutally honest, humorous feedback with personality
}


# ==================
# Request/Response Models
# ==================

class AuditRequest(BaseModel):
    """Request body for QA audit"""
    url: str
    mode: Literal["basic", "full", "roast"] = "full"
    personality: Literal["professional", "friendly", "roast"] = "professional"


class AuditSummary(BaseModel):
    """Summary section of QA report"""
    overall_score: int
    bugs_found: int
    improvements: int


class AuditResponse(BaseModel):
    """Full QA audit response"""
    url: str
    audit_timestamp: str
    page_title: str
    load_time_ms: int
    summary: AuditSummary
    accessibility: dict
    console_errors: list
    broken_links: list
    ux_evaluation: dict
    recommendations: list
    personality_feedback: Optional[str] = None
    credits_consumed: int = 0
    error: Optional[str] = None


# ==================
# Endpoints
# ==================

@router.post("/audit/basic")
async def run_basic_audit(
    request: AuditRequest,
    current_user: "User" = Depends(require_credits(5, "QA Basic Audit")),
    db: AsyncSession = Depends(get_db),
):
    """
    Basic QA audit - 5 credits
    
    Performs:
    - Page load analysis
    - Console error detection
    - Link validation (first 10)
    """
    try:
        report = await qa_tester_agent.run_full_audit(
            url=request.url,
            mode="basic",
            personality="professional"
        )
        result = report.to_dict()
        result["credits_consumed"] = 5
        result["personality_feedback"] = None
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit failed: {str(e)}")


@router.post("/audit/full")
async def run_full_audit(
    request: AuditRequest,
    current_user: "User" = Depends(require_credits(15, "QA Full Audit")),
    db: AsyncSession = Depends(get_db),
):
    """
    Full QA audit with AI UX evaluation - 15 credits
    
    Performs:
    - Page load analysis
    - Console error detection
    - Accessibility checks
    - Link validation
    - AI-powered UX evaluation
    - Prioritized recommendations
    """
    try:
        report = await qa_tester_agent.run_full_audit(
            url=request.url,
            mode="full",
            personality=request.personality
        )
        result = report.to_dict()
        result["credits_consumed"] = 15
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit failed: {str(e)}")


@router.post("/audit/roast")
async def run_roast_audit(
    request: AuditRequest,
    current_user: "User" = Depends(require_credits(25, "QA Roast Mode")),
    db: AsyncSession = Depends(get_db),
):
    """
    🔥 ROAST MODE - 25 credits
    
    Brutally honest, humorous QA feedback that doesn't hold back.
    Like having a snarky senior developer review your app.
    
    Includes all Full Audit features PLUS:
    - Personality-driven feedback
    - Sarcastic improvement suggestions
    - Memorable critique you'll actually remember
    """
    try:
        report = await qa_tester_agent.run_full_audit(
            url=request.url,
            mode="full",
            personality="roast"
        )
        result = report.to_dict()
        result["credits_consumed"] = 25
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit failed: {str(e)}")


@router.get("/modes")
async def get_audit_modes():
    """Get available audit modes and their credit costs"""
    return {
        "modes": [
            {
                "id": "basic",
                "name": "Basic Audit",
                "credits": 5,
                "description": "Quick scan for console errors, broken links, and load time",
                "features": ["Console errors", "Link validation", "Load time"],
            },
            {
                "id": "full",
                "name": "Full QA + UX",
                "credits": 15,
                "description": "Comprehensive audit with AI-powered UX evaluation",
                "features": ["Everything in Basic", "Accessibility", "AI UX Scoring", "Recommendations"],
            },
            {
                "id": "roast",
                "name": "🔥 Roast Mode",
                "credits": 25,
                "description": "Brutally honest feedback with personality and humor",
                "features": ["Everything in Full", "Personality-driven feedback", "Sarcastic suggestions", "Memorable critique"],
            },
        ],
        "personalities": ["professional", "friendly", "roast"],
    }


@router.get("/health")
async def qa_health():
    """Check QA agent health"""
    return {"status": "ready", "agent": "qa_tester", "modes": list(CREDIT_COSTS.keys())}
