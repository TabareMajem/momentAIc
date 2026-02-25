"""
Cross-Startup Intelligence Service
Aggregates anonymized, successful agent outcomes across all startups on the platform
to create industry-level "Hive Mind" playbooks and insights.
"""

from typing import Dict, Any, List, Optional
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.startup import Startup
from app.models.agent_memory import AgentOutcome, OutcomeStatus

logger = structlog.get_logger()

class CrossStartupIntelligenceService:
    """
    Computes and retrieves aggregated ecosystem learnings.
    """
    
    async def get_industry_insights(
        self, 
        db: AsyncSession, 
        industry: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieves the top successful agent actions for a specific industry.
        """
        # We want to find the most common 'successful' actions for this industry
        # Join AgentOutcome with Startup to filter by industry
        stmt = (
            select(
                AgentOutcome.agent_name,
                AgentOutcome.action_type,
                func.count().label('success_count')
            )
            .join(Startup, AgentOutcome.startup_id == Startup.id)
            .where(
                Startup.industry == industry,
                AgentOutcome.outcome_status == OutcomeStatus.successful
            )
            .group_by(AgentOutcome.agent_name, AgentOutcome.action_type)
            .order_by(func.count().desc())
            .limit(limit)
        )
        
        result = await db.execute(stmt)
        rows = result.all()
        
        insights = []
        for row in rows:
            insights.append({
                "agent_name": row.agent_name,
                "action_type": row.action_type,
                "success_count": row.success_count,
                "message": f"The {row.agent_name} has successfully executed '{row.action_type}' {row.success_count} times for other {industry} startups."
            })
            
        return insights

    
    async def format_insights_for_prompt(
        self, 
        db: AsyncSession, 
        industry: str
    ) -> str:
        """
        Format the insights into a string block for LLM system prompts.
        """
        insights = await self.get_industry_insights(db, industry)
        
        if not insights:
            return ""
            
        lines = [
            "=========================================",
            "🌐 GLOBAL HIVE MIND: CROSS-STARTUP INSIGHTS",
            f"Based on anonymized data from other {industry} startups on Momentaic:",
            "========================================="
        ]
        
        for idx, insight in enumerate(insights, 1):
            lines.append(f"{idx}. {insight['message']}")
            
        lines.append("Use these proven ecosystem patterns to guide your strategy.")
        
        return "\n".join(lines)


# Singleton
cross_startup_intelligence = CrossStartupIntelligenceService()
