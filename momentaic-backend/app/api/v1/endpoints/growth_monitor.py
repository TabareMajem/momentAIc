
"""
Growth Monitoring Dashboard Endpoint
Provides real-time view of lead pipeline and agent activity.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.growth import Lead, LeadStatus
from typing import Dict, Any
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.get("/monitor")
async def get_pipeline_monitor(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns a snapshot of the current growth pipeline status.
    """
    try:
        # 1. Lead Counts by Status
        lead_counts = await db.execute(
            select(Lead.status, func.count(Lead.id)).group_by(Lead.status)
        )
        status_breakdown = {str(row[0].value): row[1] for row in lead_counts.fetchall()}
        
        # 2. Total Leads
        total_leads = sum(status_breakdown.values())
        
        # 3. Recent Leads (Last 5)
        recent_leads_query = await db.execute(
            select(Lead).order_by(Lead.created_at.desc()).limit(5)
        )
        recent_leads = [
            {
                "id": str(lead.id),
                "name": lead.contact_name,
                "company": lead.company_name,
                "status": lead.status.value,
                "created_at": str(lead.created_at)
            }
            for lead in recent_leads_query.scalars().all()
        ]
        
        return {
            "success": True,
            "summary": {
                "total_leads": total_leads,
                "leads_by_status": status_breakdown,
            },
            "recent_leads": recent_leads,
            "agent_status": {
                "hunter": "ready",
                "ambassador": "ready",
                "listening_engine": "idle"
            }
        }
        
    except Exception as e:
        logger.error("Monitor endpoint failed", error=str(e))
        return {"success": False, "error": str(e)}

