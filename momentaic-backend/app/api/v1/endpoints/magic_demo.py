"""
Magic Demo API Endpoint
Chains real AI agents to deliver live GTM analysis from a URL.
This replaces the frontend's setTimeout simulation with real LLM-powered output.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import structlog
import asyncio

from app.agents.base import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

logger = structlog.get_logger()

router = APIRouter()


class MagicDemoRequest(BaseModel):
    url: str = Field(..., description="Website URL to analyze")


class MagicDemoResponse(BaseModel):
    url: str
    icp_analysis: Dict[str, Any] = {}
    viral_hooks: list = []
    linkedin_posts: list = []
    cold_email: str = ""
    growth_blueprint: Dict[str, Any] = {}
    error: Optional[str] = None


@router.post("/magic-demo", response_model=MagicDemoResponse)
async def run_magic_demo(request: MagicDemoRequest):
    """
    Run the 60-second Magic Demo using real AI agents.
    
    Chain:
    1. Scrape the URL and analyze ICP (GrowthHacker)
    2. Generate 3 viral Twitter hooks (LLM)
    3. Generate 2 LinkedIn posts (LLM)
    4. Draft a cold email sequence (LLM)
    5. Compile growth blueprint summary
    """
    url = request.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    logger.info("magic_demo_start", url=url)

    result = MagicDemoResponse(url=url)

    try:
        llm = get_llm("gemini-2.0-flash", temperature=0.7)
        if not llm:
            raise HTTPException(status_code=500, detail="LLM not available")
    except Exception as e:
        logger.error("magic_demo_llm_init_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"LLM initialization failed: {str(e)}")

    # ── Step 1: Scrape & Analyze ICP ──
    try:
        scraped_content = ""
        try:
            from app.agents.browser_agent import browser_agent
            nav_result = await browser_agent.navigate(url)
            if nav_result.success:
                scraped_content = nav_result.text_content[:6000]
        except Exception as e:
            logger.warning("magic_demo_scrape_failed", url=url, error=str(e))
            scraped_content = f"(Scraping failed for {url})"

        icp_prompt = f"""Analyze this website for a go-to-market strategy.

URL: {url}
Website Content: {scraped_content[:4000]}

Return ONLY valid JSON (no markdown fences):
{{
    "company_name": "extracted or inferred company name",
    "what_they_do": "1-sentence product description",
    "target_audience": "Most lucrative customer segment",
    "pain_point": "The core problem they solve",
    "competitive_advantage": "What makes them different",
    "industry": "Industry classification",
    "stage": "startup stage estimate (pre-seed/seed/series-a/growth)"
}}"""

        icp_response = await llm.ainvoke([
            SystemMessage(content="You are a startup analyst. Return ONLY raw JSON, no markdown."),
            HumanMessage(content=icp_prompt)
        ])

        import json, re
        content = re.sub(r'```json\s*', '', icp_response.content)
        content = re.sub(r'```\s*', '', content)
        result.icp_analysis = json.loads(content)

    except Exception as e:
        logger.warning("magic_demo_icp_failed", error=str(e))
        result.icp_analysis = {
            "company_name": url.split("//")[-1].split("/")[0],
            "what_they_do": "Analysis in progress",
            "error": str(e)
        }

    # ── Step 2: Generate 3 Viral Twitter Hooks ──
    try:
        company_context = json.dumps(result.icp_analysis, default=str)
        hooks_prompt = f"""Based on this company analysis:
{company_context}

Generate 3 viral Twitter/X hooks that would drive massive engagement.
Each hook should be scroll-stopping, contrarian or curiosity-driven.

Return ONLY a JSON array of strings, no markdown:
["hook 1 text here", "hook 2 text here", "hook 3 text here"]"""

        hooks_response = await llm.ainvoke([
            SystemMessage(content="You are a viral content strategist. Return ONLY raw JSON."),
            HumanMessage(content=hooks_prompt)
        ])

        content = re.sub(r'```json\s*', '', hooks_response.content)
        content = re.sub(r'```\s*', '', content)
        result.viral_hooks = json.loads(content)

    except Exception as e:
        logger.warning("magic_demo_hooks_failed", error=str(e))
        result.viral_hooks = ["Hook generation failed"]

    # ── Step 3: Generate 2 LinkedIn Posts ──
    try:
        linkedin_prompt = f"""Based on this company:
{company_context}

Write 2 LinkedIn posts that would generate engagement and establish thought leadership.
Each post should be 3-5 paragraphs, include emojis, and end with a call-to-action.

Return ONLY a JSON array of strings (each string is a full post), no markdown:
["Full post 1 text here...", "Full post 2 text here..."]"""

        linkedin_response = await llm.ainvoke([
            SystemMessage(content="You are a LinkedIn growth expert. Return ONLY raw JSON array."),
            HumanMessage(content=linkedin_prompt)
        ])

        content = re.sub(r'```json\s*', '', linkedin_response.content)
        content = re.sub(r'```\s*', '', content)
        result.linkedin_posts = json.loads(content)

    except Exception as e:
        logger.warning("magic_demo_linkedin_failed", error=str(e))
        result.linkedin_posts = ["LinkedIn post generation failed"]

    # ── Step 4: Draft Cold Email ──
    try:
        email_prompt = f"""Based on this company:
{company_context}

Write a compelling cold email sequence (just the first email) that an SDR would send to a potential customer.
Include:
- A personalized subject line
- A 3-paragraph body that leads with the prospect's pain point
- A soft CTA (not pushy)

Return the email as a single string with proper formatting.
Return ONLY the email text, no JSON wrapping, no markdown fences."""

        email_response = await llm.ainvoke([
            SystemMessage(content="You are an elite SDR copywriter. Write emails that get replies."),
            HumanMessage(content=email_prompt)
        ])

        result.cold_email = email_response.content.strip()

    except Exception as e:
        logger.warning("magic_demo_email_failed", error=str(e))
        result.cold_email = "Cold email generation failed"

    # ── Step 5: Compile Growth Blueprint ──
    result.growth_blueprint = {
        "url": url,
        "assets_generated": len(result.viral_hooks) + len(result.linkedin_posts) + (1 if result.cold_email else 0),
        "icp_identified": bool(result.icp_analysis.get("target_audience")),
        "recommendation": f"Focus on {result.icp_analysis.get('target_audience', 'your ideal customer')} — "
                         f"lead with the pain point: {result.icp_analysis.get('pain_point', 'their core problem')}."
    }

    logger.info("magic_demo_complete", url=url, assets=result.growth_blueprint["assets_generated"])
    return result
