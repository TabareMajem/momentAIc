
import base64
import structlog
import httpx
from typing import Dict, Any, Optional

logger = structlog.get_logger()

class GithubService:
    """
    Service to interact with GitHub API for "One-Click Import"
    """
    
    BASE_URL = "https://api.github.com"
    
    async def fetch_repo_context(self, repo_url: str) -> Dict[str, Any]:
        """
        Fetch README and basic metadata from a public GitHub repo.
        Returns a context dict suitable for the GrowthHacker agent.
        """
        # 1. Parse URL to get owner/repo
        # formats: https://github.com/owner/repo, https://github.com/owner/repo.git
        clean_url = repo_url.rstrip(".git")
        try:
            parts = clean_url.split("github.com/")[-1].split("/")
            owner = parts[0]
            repo = parts[1]
        except Exception:
            return {"error": "Invalid GitHub URL format"}
            
        logger.info("Fetching GitHub repo", owner=owner, repo=repo)
        
        context = {
            "name": repo,
            "url": repo_url,
            "source": "github_import",
            "readme_content": "",
            "description": "",
            "topics": []
        }
        
        async with httpx.AsyncClient() as client:
            # 2. Get Repo Details (Description, Topics)
            try:
                repo_resp = await client.get(f"{self.BASE_URL}/repos/{owner}/{repo}")
                if repo_resp.status_code == 200:
                    data = repo_resp.json()
                    context["description"] = data.get("description", "")
                    context["topics"] = data.get("topics", [])
                    context["stars"] = data.get("stargazers_count", 0)
                    context["language"] = data.get("language", "Unknown")
            except Exception as e:
                logger.error("Failed to fetch repo details", error=str(e))

            # 3. Get README
            try:
                # GitHub API returns content as base64
                readme_resp = await client.get(f"{self.BASE_URL}/repos/{owner}/{repo}/readme")
                if readme_resp.status_code == 200:
                    data = readme_resp.json()
                    content_b64 = data.get("content", "")
                    # Decode
                    context["readme_content"] = base64.b64decode(content_b64).decode("utf-8")
            except Exception as e:
                logger.error("Failed to fetch README", error=str(e))
                
        # Truncate README if too large (protect context window)
        if len(context["readme_content"]) > 20000:
            context["readme_content"] = context["readme_content"][:20000] + "...(truncated)"
            
        return context

github_service = GithubService()
