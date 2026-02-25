
from typing import Dict, Any, Optional
import structlog
from app.services.github_service import github_service
from app.agents.browser_agent import browser_agent

logger = structlog.get_logger()

class ImportService:
    """
    Universal Import Service for "God Mode" Execution.
    Ingests content from various sources (GitHub, Web, Documents) 
    and normalizes it for the Strategy Engine.
    """
    
    async def import_from_source(self, source_type: str, url: str, extra_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main entry point for importing context.
        
        Args:
            source_type: 'github', 'web', 'doc'
            url: The URL or path to the source
            extra_data: Any additional metadata (e.g. branch name, auth tokens)
            
        Returns:
            Dict containing standardized context:
            {
                "name": str,
                "description": str,
                "content": str, # Full text/code content
                "source_metadata": Dict
            }
        """
        logger.info("ImportService: Starting import", type=source_type, url=url)
        
        if source_type == "github":
            return await self._import_github(url)
        elif source_type == "web":
            return await self._import_web(url)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

    async def _import_github(self, url: str) -> Dict[str, Any]:
        """Import from GitHub using existing service"""
        repo_context = await github_service.fetch_repo_context(url)
        
        if "error" in repo_context:
            raise ValueError(repo_context["error"])
            
        return {
            "name": repo_context.get("name", "Unknown Repo"),
            "description": repo_context.get("description", ""),
            "content": repo_context.get("readme_content", ""),
            "source_metadata": {
                "source": "github",
                "topics": repo_context.get("topics", []),
                "stars": repo_context.get("stars", 0),
                "language": repo_context.get("language", "Unknown"),
                "url": url
            }
        }

    async def _import_web(self, url: str) -> Dict[str, Any]:
        """Import from a Product/Landing Page using BrowserAgent"""
        result = await browser_agent.navigate(url)
        
        if not result.success:
            raise ValueError(f"Failed to scrape URL: {result.error}")
        
        # Basic inference of name from URL/Title
        # In a real app, we might use an LLM here to extract deeper metadata
        # For now, we trust the scraping result
        
        return {
            "name": self._extract_name_from_url(url),
            "description": "Imported from website",
            "content": result.text_content[:20000],  # Limit content size
            "source_metadata": {
                "source": "web",
                "title": result.title,
                "url": url,
                "screenshot": result.screenshot  # preserve path if we want to show it
            }
        }
    
    def _extract_name_from_url(self, url: str) -> str:
        """Simple heuristic to get a readable name from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            if "www." in domain:
                domain = domain.replace("www.", "")
            return domain.split(".")[0].title()
        except Exception:
            return "Unknown Website"

import_service = ImportService()
