"""
Browser Prospector Agent
Specialized agent for executing outbound prospecting loops natively in the browser (e.g., Sales Navigator).
Bypasses API limits by orchestrating a headless browser context loaded from the Credentials Vault.

Improvements over V1:
  - Lead deduplication via LinkedIn URL matching
  - Multi-page scroll with configurable depth
  - Graceful error recovery with partial results
  - ICP-to-boolean conversion via LLM
  - Structured logging at every step
"""

from typing import Dict, Any, List, Optional
import structlog
import asyncio
import json
import urllib.parse
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.growth import Lead, LeadSource, LeadStatus
from app.agents.browser_agent import browser_agent
from app.agents.base import BaseAgent
from app.core.config import settings

logger = structlog.get_logger()


class BrowserProspectorAgent(BaseAgent):
    """
    Browser Prospector Agent v2
    Executes Sales Navigator or standard LinkedIn searches directly via Playwright/OpenClaw.
    Extracts leads natively, deduplicates against existing CRM, and saves new ones.
    """

    def __init__(self):
        self.name = "Browser Prospector"
        self.role = "Head of Outbound Sourcing"
        self.goal = "Identify and extract high-quality leads natively via browser automation."
        self.capabilities = ["web_browsing", "lead_generation", "data_extraction"]

    async def _translate_icp_to_query(self, icp_prompt: str) -> str:
        """Use LLM to convert natural language ICP into a LinkedIn boolean search string."""
        llm = self.get_llm()
        prompt = (
            "Convert this Ideal Customer Profile into a LinkedIn boolean search query.\n"
            f"ICP: {icp_prompt}\n"
            "Return ONLY the keyword string. Example: CTO AND FinTech AND \"New York\"\n"
            "Do not wrap in quotes. Do not add explanation."
        )
        response = await llm.ainvoke(prompt)
        return response.content.strip().replace('"', '')

    async def _get_existing_linkedin_urls(self, db: AsyncSession, startup_id: UUID) -> set:
        """Fetch all existing LinkedIn URLs for deduplication."""
        result = await db.execute(
            select(Lead.contact_linkedin)
            .where(Lead.startup_id == startup_id, Lead.contact_linkedin.isnot(None))
        )
        return {row[0] for row in result.all() if row[0]}

    async def _extract_leads_from_page(self, page_content: str, limit: int) -> List[Dict]:
        """Parse raw DOM content via LLM to extract structured lead data."""
        llm = self.get_llm()
        extraction_prompt = f"""Extract up to {limit} leads from this LinkedIn profile search results page.
Return ONLY a raw JSON array of objects with keys:
  "contact_name" (string, full name),
  "contact_title" (string, job title),
  "company_name" (string, or "Unknown"),
  "contact_linkedin" (string, profile URL or empty string).

Rules:
- Do NOT wrap in markdown code blocks.
- If no leads are found, return an empty array: []
- If company name isn't clear, use "Unknown".

Page Content:
{page_content[:20000]}"""

        response = await llm.ainvoke(extraction_prompt)
        raw = response.content.strip()

        # Strip markdown fences if present
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]

        try:
            data = json.loads(raw.strip())
            return data if isinstance(data, list) else [data]
        except json.JSONDecodeError as e:
            logger.error("LLM lead extraction parse failed", error=str(e), snippet=raw[:200])
            return []

    async def run_sales_nav_loop(
        self,
        db: AsyncSession,
        user_id: str,
        startup_id: UUID,
        icp_prompt: str,
        limit: int = 50,
        max_pages: int = 3
    ) -> Dict[str, Any]:
        """
        Executes a targeted LinkedIn search based on an ICP prompt.
        Loads the user's saved session, navigates, extracts, deduplicates, and saves.
        """
        logger.info("browser_prospector.start", user_id=user_id, icp=icp_prompt, limit=limit)
        run_start = datetime.utcnow()

        # 1. Load authenticated browser session
        try:
            has_session = await browser_agent.load_session(user_id=str(user_id))
        except Exception as e:
            logger.error("browser_prospector.session_load_failed", error=str(e))
            has_session = False

        if not has_session:
            return {
                "success": False,
                "error": "No authenticated browser session found. Connect your LinkedIn account in Settings → Integrations."
            }

        # 2. Translate ICP → boolean query
        search_query = await self._translate_icp_to_query(icp_prompt)
        encoded_query = urllib.parse.quote(search_query)
        base_url = f"https://www.linkedin.com/search/results/people/?keywords={encoded_query}"

        logger.info("browser_prospector.query_generated", query=search_query, url=base_url)

        # 3. Get existing LinkedIn URLs for dedup
        existing_urls = await self._get_existing_linkedin_urls(db, startup_id)
        logger.info("browser_prospector.dedup_loaded", existing_count=len(existing_urls))

        # 4. Navigate and extract across pages
        all_leads: List[Dict] = []
        errors: List[str] = []

        for page_num in range(1, max_pages + 1):
            if len(all_leads) >= limit:
                break

            page_url = f"{base_url}&page={page_num}" if page_num > 1 else base_url

            try:
                nav_result = await browser_agent.navigate(page_url, wait_for="networkidle")
                if not nav_result.success:
                    errors.append(f"Page {page_num}: Navigation failed - {nav_result.error}")
                    continue

                page_leads = await self._extract_leads_from_page(
                    nav_result.text_content or "",
                    limit - len(all_leads)
                )
                all_leads.extend(page_leads)
                logger.info("browser_prospector.page_extracted", page=page_num, leads_on_page=len(page_leads))

                # Small delay between pages to avoid rate limit
                if page_num < max_pages:
                    await asyncio.sleep(2)

            except Exception as e:
                errors.append(f"Page {page_num}: {str(e)[:100]}")
                logger.error("browser_prospector.page_error", page=page_num, error=str(e))

        # 5. Deduplicate and save
        saved_count = 0
        skipped_count = 0

        for lead_dict in all_leads:
            if saved_count >= limit:
                break

            name = lead_dict.get("contact_name", "").strip()
            if not name:
                continue

            linkedin_url = lead_dict.get("contact_linkedin", "").strip()

            # Dedup check
            if linkedin_url and linkedin_url in existing_urls:
                skipped_count += 1
                continue

            lead = Lead(
                startup_id=startup_id,
                contact_name=name,
                contact_title=lead_dict.get("contact_title", ""),
                company_name=lead_dict.get("company_name", "Unknown"),
                contact_linkedin=linkedin_url or None,
                source=LeadSource.LINKEDIN,
                status=LeadStatus.NEW,
                probability=15,
                research_data={
                    "icp_matched": icp_prompt,
                    "search_query": search_query,
                    "extracted_at": datetime.utcnow().isoformat()
                }
            )
            db.add(lead)
            saved_count += 1

            if linkedin_url:
                existing_urls.add(linkedin_url)

        await db.commit()

        duration_ms = int((datetime.utcnow() - run_start).total_seconds() * 1000)
        logger.info(
            "browser_prospector.complete",
            saved=saved_count, skipped=skipped_count,
            total_extracted=len(all_leads), duration_ms=duration_ms
        )

        return {
            "success": True,
            "leads_found": saved_count,
            "leads_skipped_dedup": skipped_count,
            "total_extracted": len(all_leads),
            "search_query": search_query,
            "target_url": base_url,
            "pages_scanned": min(max_pages, len(all_leads) // 10 + 1),
            "duration_ms": duration_ms,
            "errors": errors if errors else None
        }

    async def process(self, message: str, startup_context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return {
            "response": (
                "I'm the Browser Prospector. Send me a target ICP like "
                "\"FinTech CTOs in New York\" and I'll execute a headless browser loop "
                "to scrape matching leads directly into your CRM — bypassing all API limits."
            ),
            "agent": self.name
        }
