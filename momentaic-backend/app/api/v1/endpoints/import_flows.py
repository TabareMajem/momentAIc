
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.startup import ImportGithubRequest
from app.services.github_service import github_service
from app.agents.growth_hacker_agent import growth_hacker_agent
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.post("/github", response_model=Dict[str, Any])
async def import_from_github(
    request: ImportGithubRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Import a startup context from a GitHub repository.
    Fetches README, analyzes it with GrowthHacker agent, and returns a strategy.
    """
    try:
        # 1. Fetch Repo Context
        repo_context = await github_service.fetch_repo_context(request.repo_url)
        
        if "error" in repo_context:
            raise HTTPException(status_code=400, detail=repo_context["error"])
            
        # 2. Analyze with Growth Hacker
        # We pass the README as the description to give the agent full context
        description = f"GitHub Repository: {repo_context['name']}\n\nOverview: {repo_context['description']}\n\nREADME Content:\n{repo_context.get('readme_content', '')[:15000]}"
        
        analysis = await growth_hacker_agent.analyze_startup_wizard(
            url=request.repo_url,
            description=description
        )
        
        if "error" in analysis:
            raise HTTPException(status_code=500, detail=analysis["error"])
            
        # 3. Return Combined Result
        return {
            "source": "github",
            "repo_details": {
                "name": repo_context["name"],
                "description": repo_context["description"],
                "topics": repo_context["topics"],
                "stars": repo_context.get("stars", 0)
            },
            "strategy": analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("GitHub import failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import from GitHub: {str(e)}"
        )
