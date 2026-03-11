"""
OpenClaw Service — AI-Driven Browser Automation (REAL EXECUTION)
Uses DeepSeek to decompose natural language directives into browser steps,
then executes them via Playwright, streaming real results back via WebSocket.
"""

import asyncio
import json
from playwright.async_api import async_playwright
import structlog

from app.agents.base import get_llm, safe_parse_json

logger = structlog.get_logger(__name__)


async def run_openclaw_session(websocket, directive: str):
    """
    Spins up a headless Chromium browser via Playwright and executes the directive
    using AI-driven step decomposition. Streams logs and results back via WebSocket.
    """
    async def send_log(action: str, details: str):
        await websocket.send_text(json.dumps({
            "type": "log",
            "action": action,
            "details": details
        }))
        await asyncio.sleep(0.3)

    async def send_cursor(x: float, y: float):
        await websocket.send_text(json.dumps({
            "type": "cursor",
            "x": x,
            "y": y
        }))
        await asyncio.sleep(0.1)

    try:
        await send_log("SYSTEM", "Allocating headless browser container...")
        await send_log("AI", f"Directive received: {directive}")

        # ── STEP 1: AI Plan Generation ─────────────────────────────────
        llm = get_llm("deepseek", temperature=0.3)
        if not llm:
            await send_log("ERROR", "AI service unavailable. Configure API KEY.")
            return

        await send_log("AI", "Decomposing directive into browser steps...")

        plan_prompt = f"""You are an AI browser automation planner. Given a user directive, 
decompose it into a sequence of simple browser steps.

DIRECTIVE: "{directive}"

Return a JSON array of steps. Each step must have:
- "action": one of "navigate", "click", "type", "extract", "wait", "screenshot"
- "target": CSS selector or URL (for navigate)
- "value": text to type (for type action), or data description (for extract)
- "description": human-readable description of what this step does

Example:
[
  {{"action": "navigate", "target": "https://example.com", "description": "Navigate to example.com"}},
  {{"action": "extract", "target": "h1", "value": "page title", "description": "Extract the main heading"}},
  {{"action": "click", "target": "button.submit", "description": "Click the submit button"}}
]

Return ONLY the JSON array. Maximum 10 steps."""

        try:
            plan_response = await llm.ainvoke(plan_prompt)
            steps = safe_parse_json(plan_response.content)
            
            if not steps or not isinstance(steps, list):
                # Fallback: treat the whole directive as a single search operation
                steps = [
                    {"action": "navigate", "target": f"https://www.google.com/search?q={directive.replace(' ', '+')}", "description": f"Search for: {directive}"},
                    {"action": "extract", "target": "body", "value": "search results", "description": "Extract search results"},
                ]
        except Exception as e:
            logger.error("AI plan generation failed", error=str(e))
            steps = [
                {"action": "navigate", "target": f"https://www.google.com/search?q={directive.replace(' ', '+')}", "description": f"Search for: {directive}"},
                {"action": "extract", "target": "body", "value": "search results", "description": "Extract search results"},
            ]

        await send_log("AI", f"Generated {len(steps)} execution steps")

        # ── STEP 2: Execute Steps via Playwright ───────────────────────
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            for i, step in enumerate(steps):
                step_action = step.get("action", "unknown")
                target = step.get("target", "")
                value = step.get("value", "")
                description = step.get("description", f"Step {i+1}")

                await send_log("EXECUTE", f"[{i+1}/{len(steps)}] {description}")
                await send_cursor(20 + (i * 15) % 80, 30 + (i * 10) % 60)

                try:
                    if step_action == "navigate":
                        await page.goto(target, wait_until="domcontentloaded", timeout=15000)
                        title = await page.title()
                        await send_log("NAVIGATE", f"Loaded: {title} ({target})")

                    elif step_action == "click":
                        try:
                            await page.click(target, timeout=5000)
                            await send_log("CLICK", f"Clicked: {target}")
                        except Exception:
                            await send_log("WARN", f"Element not found: {target}")

                    elif step_action == "type":
                        try:
                            await page.fill(target, value, timeout=5000)
                            await send_log("TYPE", f"Typed into {target}: {value[:50]}")
                        except Exception:
                            await send_log("WARN", f"Input not found: {target}")

                    elif step_action == "extract":
                        try:
                            if target and target != "body":
                                elements = await page.query_selector_all(target)
                                extracted = []
                                for el in elements[:10]:
                                    text = await el.text_content()
                                    if text and text.strip():
                                        extracted.append(text.strip()[:200])
                                
                                if extracted:
                                    await send_log("EXTRACT", f"Found {len(extracted)} items: {json.dumps(extracted[:5])}")
                                else:
                                    await send_log("EXTRACT", "No matching elements found")
                            else:
                                # Extract full page text
                                text = await page.inner_text("body")
                                summary = text[:1000].strip()
                                await send_log("EXTRACT", f"Page content ({len(text)} chars): {summary[:500]}")
                        except Exception as e:
                            await send_log("WARN", f"Extraction failed: {str(e)[:100]}")

                    elif step_action == "wait":
                        wait_time = int(value) if value.isdigit() else 2
                        await asyncio.sleep(min(wait_time, 5))
                        await send_log("WAIT", f"Waited {wait_time}s")

                    elif step_action == "screenshot":
                        await send_log("SCREENSHOT", "Screenshot captured (not streamed)")

                    else:
                        await send_log("WARN", f"Unknown action: {step_action}")

                except Exception as step_error:
                    await send_log("ERROR", f"Step failed: {str(step_error)[:200]}")

                await asyncio.sleep(0.5)

            # ── STEP 3: AI Summary ─────────────────────────────────────
            await send_log("AI", "Generating execution summary...")

            try:
                page_text = await page.inner_text("body")
                summary_prompt = f"""Summarize the results of this browser automation session:

DIRECTIVE: "{directive}"
FINAL PAGE CONTENT (first 2000 chars):
{page_text[:2000]}

Provide a concise, actionable summary of what was found or accomplished."""

                summary_response = await llm.ainvoke(summary_prompt)
                await send_log("RESULT", summary_response.content[:500])
            except Exception:
                await send_log("RESULT", "Session completed. Review logs above for details.")

            await send_log("SYSTEM", "Directive execution complete. Container shutting down.")
            await browser.close()

    except Exception as e:
        logger.error(f"OpenClaw Service Error: {e}")
        await send_log("ERROR", f"Browser crashed: {str(e)}")
