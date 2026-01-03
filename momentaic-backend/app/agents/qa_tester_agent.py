"""
QA & Tester Agent
Automated app auditing, bug detection, and UX evaluation
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import structlog
import asyncio
import re

from app.agents.base import get_llm

logger = structlog.get_logger()


@dataclass
class AccessibilityIssue:
    """Single accessibility issue"""
    type: str  # e.g., "missing_alt", "low_contrast", "no_aria"
    element: str
    severity: str  # "critical", "major", "minor"
    suggestion: str


@dataclass
class BrokenLink:
    """Broken link detected during audit"""
    url: str
    text: str
    status_code: int
    error: Optional[str] = None


@dataclass
class ConsoleError:
    """Browser console error"""
    level: str  # "error", "warning"
    message: str
    source: Optional[str] = None


@dataclass
class Recommendation:
    """Improvement recommendation"""
    priority: str  # "critical", "high", "medium", "low"
    category: str  # "bug", "ux", "performance", "accessibility", "seo"
    description: str
    fix_suggestion: str


@dataclass
class QAReport:
    """Comprehensive QA audit report"""
    url: str
    audit_timestamp: str
    page_title: str = ""
    load_time_ms: int = 0
    overall_score: int = 0
    
    # Detailed findings
    accessibility_score: int = 0
    accessibility_issues: List[AccessibilityIssue] = field(default_factory=list)
    console_errors: List[ConsoleError] = field(default_factory=list)
    broken_links: List[BrokenLink] = field(default_factory=list)
    
    # UX Evaluation
    ux_score: int = 0
    ux_notes: str = ""
    
    # Recommendations
    recommendations: List[Recommendation] = field(default_factory=list)
    
    # Summary
    bugs_found: int = 0
    improvements_suggested: int = 0
    
    # Personality feedback (for roast/friendly modes)
    personality_feedback: str = ""
    
    screenshot_url: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        return {
            "url": self.url,
            "audit_timestamp": self.audit_timestamp,
            "page_title": self.page_title,
            "load_time_ms": self.load_time_ms,
            "audit_timestamp": self.audit_timestamp,
            "page_title": self.page_title,
            "load_time_ms": self.load_time_ms,
            "screenshot_url": self.screenshot_url,
            "summary": {
                "overall_score": self.overall_score,
                "bugs_found": self.bugs_found,
                "improvements": self.improvements_suggested,
            },
            "accessibility": {
                "score": self.accessibility_score,
                "issues": [
                    {"type": i.type, "element": i.element, "severity": i.severity, "suggestion": i.suggestion}
                    for i in self.accessibility_issues
                ],
            },
            "console_errors": [
                {"level": e.level, "message": e.message, "source": e.source}
                for e in self.console_errors
            ],
            "broken_links": [
                {"url": l.url, "text": l.text, "status_code": l.status_code, "error": l.error}
                for l in self.broken_links
            ],
            "ux_evaluation": {
                "score": self.ux_score,
                "notes": self.ux_notes,
            },
            "recommendations": [
                {"priority": r.priority, "category": r.category, "description": r.description, "fix_suggestion": r.fix_suggestion}
                for r in self.recommendations
            ],
            "personality_feedback": self.personality_feedback,
            "error": self.error,
        }


class QATesterAgent:
    """
    QA & Tester Agent - Automated app auditing
    
    Capabilities:
    - Full page audit (load time, title, meta, structure)
    - Console error detection
    - Accessibility evaluation
    - Link validation
    - AI-powered UX scoring
    - Prioritized improvement recommendations
    """
    
    def __init__(self):
        self._browser = None
        self._context = None
        self._page = None
        self._console_errors: List[ConsoleError] = []
    
    async def initialize(self):
        """Initialize headless browser"""
        if self._browser:
            return
        
        try:
            from playwright.async_api import async_playwright
            
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                ]
            )
            self._context = await self._browser.new_context(
                user_agent="MomentAIc-QA-Tester/1.0",
                viewport={"width": 1920, "height": 1080},
            )
            self._page = await self._context.new_page()
            
            # Capture console errors
            self._page.on("console", self._handle_console)
            
            logger.info("QA Browser initialized")
        except ImportError:
            logger.warning("Playwright not installed for QA agent")
            self._browser = None
    
    def _handle_console(self, msg):
        """Capture console messages"""
        if msg.type in ("error", "warning"):
            self._console_errors.append(ConsoleError(
                level=msg.type,
                message=msg.text[:500],
                source=msg.location.get("url") if hasattr(msg, "location") else None,
            ))
    
    async def run_full_audit(self, url: str, mode: str = "full", personality: str = "professional") -> QAReport:
        """
        Run a comprehensive QA audit on the given URL
        
        Args:
            url: The URL to audit
            mode: "basic" or "full" - determines depth of analysis
            personality: "professional", "friendly", or "roast" - feedback style
        """
        await self.initialize()
        self._console_errors = []  # Reset
        
        report = QAReport(
            url=url,
            audit_timestamp=datetime.utcnow().isoformat() + "Z",
        )
        
        if not self._browser:
            report.error = "Browser service unavailable. Playwright may not be installed."
            return report
        
        try:
            # 1. Navigate and capture load time
            start_time = asyncio.get_event_loop().time()
            response = await self._page.goto(url, wait_until="networkidle", timeout=30000)
            load_time = int((asyncio.get_event_loop().time() - start_time) * 1000)
            
            report.load_time_ms = load_time
            
            if not response or not response.ok:
                report.error = f"Failed to load page: HTTP {response.status if response else 'No response'}"
                return report
            
            # 2. Basic page info
            report.page_title = await self._page.title()
            
            # 3. Console errors (already captured via event)
            report.console_errors = self._console_errors.copy()
            
            # 4. Accessibility check (full mode only)
            if mode == "full":
                await self._check_accessibility(report)
            
            # 5. Link validation
            await self._validate_links(report)
            
            # 6. UX Evaluation via AI (full mode only)
            if mode == "full":
                await self._evaluate_ux(report, personality)
            
            # 7. Generate recommendations
            await self._generate_recommendations(report)
            
            # 8. Generate personality feedback (for friendly/roast modes)
            if personality in ("friendly", "roast"):
                await self._generate_personality_feedback(report, personality)
            
            # 9. Calculate overall score
            self._calculate_overall_score(report)
            
            logger.info("QA audit completed", url=url, score=report.overall_score, personality=personality)
            
        except Exception as e:
            logger.error("QA audit failed", url=url, error=str(e))
            report.error = str(e)
        
        return report
    
    async def _check_accessibility(self, report: QAReport):
        """Check for common accessibility issues"""
        try:
            # Check for images without alt text
            images_without_alt = await self._page.evaluate("""
                () => Array.from(document.querySelectorAll('img:not([alt])')).slice(0, 10).map(img => img.src.slice(-50))
            """)
            for src in images_without_alt:
                report.accessibility_issues.append(AccessibilityIssue(
                    type="missing_alt",
                    element=f"<img src='...{src}'>",
                    severity="major",
                    suggestion="Add descriptive alt text to this image",
                ))
            
            # Check for buttons without accessible text
            empty_buttons = await self._page.evaluate("""
                () => Array.from(document.querySelectorAll('button')).filter(b => !b.innerText.trim() && !b.getAttribute('aria-label')).length
            """)
            if empty_buttons > 0:
                report.accessibility_issues.append(AccessibilityIssue(
                    type="empty_button",
                    element=f"{empty_buttons} button(s)",
                    severity="major",
                    suggestion="Add text content or aria-label to buttons",
                ))
            
            # Check for missing form labels
            inputs_without_labels = await self._page.evaluate("""
                () => Array.from(document.querySelectorAll('input:not([type=hidden]):not([type=submit])')).filter(i => !i.id || !document.querySelector(`label[for="${i.id}"]`)).length
            """)
            if inputs_without_labels > 0:
                report.accessibility_issues.append(AccessibilityIssue(
                    type="missing_label",
                    element=f"{inputs_without_labels} input(s)",
                    severity="major",
                    suggestion="Associate labels with form inputs using 'for' attribute",
                ))
            
            # Calculate accessibility score
            total_issues = len(report.accessibility_issues)
            if total_issues == 0:
                report.accessibility_score = 100
            elif total_issues < 3:
                report.accessibility_score = 80
            elif total_issues < 6:
                report.accessibility_score = 60
            else:
                report.accessibility_score = 40
                
        except Exception as e:
            logger.warning("Accessibility check failed", error=str(e))
    
    async def _validate_links(self, report: QAReport):
        """Validate all links on the page"""
        try:
            links = await self._page.evaluate("""
                () => Array.from(document.querySelectorAll('a[href]')).slice(0, 30).map(a => ({
                    href: a.href,
                    text: a.innerText.slice(0, 50)
                }))
            """)
            
            import httpx
            async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                for link in links:
                    href = link.get("href", "")
                    if not href or href.startswith("javascript:") or href.startswith("#") or href.startswith("mailto:"):
                        continue
                    
                    try:
                        resp = await client.head(href)
                        if resp.status_code >= 400:
                            report.broken_links.append(BrokenLink(
                                url=href,
                                text=link.get("text", ""),
                                status_code=resp.status_code,
                            ))
                    except Exception as link_err:
                        report.broken_links.append(BrokenLink(
                            url=href,
                            text=link.get("text", ""),
                            status_code=0,
                            error=str(link_err)[:100],
                        ))
                        
        except Exception as e:
            logger.warning("Link validation failed", error=str(e))
    
    async def _evaluate_ux(self, report: QAReport, personality: str = "professional"):
        """AI-powered UX evaluation with personality"""
        try:
            # Get page structure summary
            structure = await self._page.evaluate("""
                () => ({
                    h1_count: document.querySelectorAll('h1').length,
                    h2_count: document.querySelectorAll('h2').length,
                    button_count: document.querySelectorAll('button').length,
                    form_count: document.querySelectorAll('form').length,
                    image_count: document.querySelectorAll('img').length,
                    link_count: document.querySelectorAll('a').length,
                    has_nav: document.querySelector('nav') !== null,
                    has_footer: document.querySelector('footer') !== null,
                    body_text_length: document.body.innerText.length,
                })
            """)
            
            # Take screenshot for AI analysis and live view
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"qa_audit_{timestamp}.png"
            static_dir = "/root/momentaic/momentaic-backend/app/static/screenshots"
            screenshot_path = f"{static_dir}/{filename}"
            
            # Ensure directory exists
            import os
            os.makedirs(static_dir, exist_ok=True)
            
            await self._page.screenshot(path=screenshot_path, full_page=False)
            
            # Set public URL
            report.screenshot_url = f"/static/screenshots/{filename}"
            
            # Use appropriate model based on personality
            model = "gemini-pro" if personality == "roast" else "gemini-flash"
            llm = get_llm(model, temperature=0.7 if personality == "roast" else 0.3)
            
            if llm:
                personality_instruction = self._get_personality_instruction(personality)
                
                prompt = f"""{personality_instruction}

Evaluate the UX of this webpage:

Page: {report.page_title}
URL: {report.url}
Load Time: {report.load_time_ms}ms
Structure: {structure}
Console Errors: {len(report.console_errors)}
Broken Links: {len(report.broken_links)}
Accessibility Issues: {len(report.accessibility_issues)}

Rate the UX from 0-100 and provide 2-3 specific observations in your assigned personality.
Format: SCORE: [number]\nNOTES: [observations]"""
                
                response = await llm.ainvoke(prompt)
                content = response.content if hasattr(response, 'content') else str(response)
                
                # Parse score
                score_match = re.search(r"SCORE:\s*(\d+)", content)
                if score_match:
                    report.ux_score = min(100, max(0, int(score_match.group(1))))
                
                # Parse notes
                notes_match = re.search(r"NOTES:\s*(.+)", content, re.DOTALL)
                if notes_match:
                    report.ux_notes = notes_match.group(1).strip()[:500]
            else:
                # Fallback scoring based on structure
                score = 70
                if structure.get("has_nav"):
                    score += 5
                if structure.get("has_footer"):
                    score += 5
                if structure.get("h1_count") == 1:
                    score += 5
                if report.load_time_ms < 2000:
                    score += 10
                if len(report.console_errors) == 0:
                    score += 5
                report.ux_score = min(100, score)
                report.ux_notes = "Automated structural analysis (AI unavailable)"
                
        except Exception as e:
            logger.warning("UX evaluation failed", error=str(e))
            report.ux_score = 50
            report.ux_notes = f"Evaluation incomplete: {str(e)[:100]}"
    
    def _get_personality_instruction(self, personality: str) -> str:
        """Get system instruction for personality"""
        if personality == "roast":
            return """You are a brutally honest, sarcastic senior developer reviewing a junior's work.
Be funny but genuinely helpful. Use humor to make your points memorable.
Examples of your style:
- "Your hero section loads in 4.2 seconds. That's slower than my grandma reading a QR code."
- "You have 3 buttons that say 'Click Here'. Click here to do WHAT? Give your buttons jobs."
- "This layout looks like it was designed by someone who learned CSS from a 2008 tutorial."

Don't be mean for no reason - make actionable points wrapped in humor."""
        elif personality == "friendly":
            return """You are an encouraging, supportive UX mentor giving feedback to a promising developer.
Be positive but honest. Frame criticism as opportunities for growth.
Examples of your style:
- "Great start! The color scheme is on point. Here's how we can make it even better..."
- "I love the ambition here! One quick win would be..."
- "You're 80% of the way there - just a few tweaks will take this to the next level."""
        else:  # professional
            return """You are a professional UX consultant providing objective analysis.
Be clear, direct, and data-driven. Focus on impact and prioritization."""
    
    async def _generate_personality_feedback(self, report: QAReport, personality: str):
        """Generate personality-driven summary feedback"""
        try:
            model = "gemini-pro"  # Use pro for better personality generation
            llm = get_llm(model, temperature=0.8)
            
            if not llm:
                return
            
            personality_instruction = self._get_personality_instruction(personality)
            
            issues_summary = []
            if report.console_errors:
                issues_summary.append(f"{len(report.console_errors)} JavaScript errors")
            if report.broken_links:
                issues_summary.append(f"{len(report.broken_links)} broken links")
            if report.accessibility_issues:
                issues_summary.append(f"{len(report.accessibility_issues)} accessibility issues")
            if report.load_time_ms > 3000:
                issues_summary.append(f"slow load time ({report.load_time_ms}ms)")
            
            prompt = f"""{personality_instruction}

Write a memorable 2-3 sentence summary of this website audit:

Site: {report.page_title} ({report.url})
Overall Score: {report.overall_score}/100
UX Score: {report.ux_score}/100
Issues Found: {', '.join(issues_summary) if issues_summary else 'None major!'}

Make it punchy and personality-driven. This is the first thing the user sees."""
            
            response = await llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            report.personality_feedback = content.strip()[:600]
            
        except Exception as e:
            logger.warning("Personality feedback generation failed", error=str(e))

    
    async def _generate_recommendations(self, report: QAReport):
        """Generate prioritized improvement recommendations"""
        
        # Critical: Console errors
        for error in report.console_errors:
            if error.level == "error":
                report.recommendations.append(Recommendation(
                    priority="critical",
                    category="bug",
                    description=f"JavaScript error: {error.message[:100]}",
                    fix_suggestion="Debug and resolve this console error to prevent user-facing issues",
                ))
                report.bugs_found += 1
        
        # High: Broken links
        for link in report.broken_links:
            report.recommendations.append(Recommendation(
                priority="high",
                category="bug",
                description=f"Broken link: {link.url[:80]} (HTTP {link.status_code})",
                fix_suggestion="Fix or remove this broken link",
            ))
            report.bugs_found += 1
        
        # Medium: Accessibility issues
        for issue in report.accessibility_issues:
            report.recommendations.append(Recommendation(
                priority="medium",
                category="accessibility",
                description=f"{issue.type}: {issue.element}",
                fix_suggestion=issue.suggestion,
            ))
            report.improvements_suggested += 1
        
        # Performance recommendations
        if report.load_time_ms > 3000:
            report.recommendations.append(Recommendation(
                priority="high",
                category="performance",
                description=f"Slow page load: {report.load_time_ms}ms",
                fix_suggestion="Optimize images, reduce JavaScript, and consider lazy loading",
            ))
            report.improvements_suggested += 1
        
        # UX recommendations based on score
        if report.ux_score < 70:
            report.recommendations.append(Recommendation(
                priority="medium",
                category="ux",
                description=f"Below-average UX score: {report.ux_score}/100",
                fix_suggestion=report.ux_notes or "Review layout and user flow",
            ))
            report.improvements_suggested += 1
    
    def _calculate_overall_score(self, report: QAReport):
        """Calculate weighted overall score"""
        weights = {
            "accessibility": 0.25,
            "ux": 0.30,
            "errors": 0.25,
            "links": 0.20,
        }
        
        # Error score (inverse of issue count)
        error_score = max(0, 100 - (len(report.console_errors) * 15))
        
        # Link score
        link_score = max(0, 100 - (len(report.broken_links) * 10))
        
        report.overall_score = int(
            report.accessibility_score * weights["accessibility"] +
            report.ux_score * weights["ux"] +
            error_score * weights["errors"] +
            link_score * weights["links"]
        )
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """Process a QA request from the agent system"""
        message_lower = message.lower()
        
        # Extract URL from message
        urls = re.findall(r'https?://\S+', message)
        
        if urls:
            report = await self.run_full_audit(urls[0])
            return {
                "response": f"QA Audit Complete for {report.page_title or report.url}\n\n"
                           f"**Overall Score**: {report.overall_score}/100\n"
                           f"**Bugs Found**: {report.bugs_found}\n"
                           f"**Improvements**: {report.improvements_suggested}\n\n"
                           f"Use the API endpoint for full JSON report.",
                "data": report.to_dict(),
                "agent": "qa_tester",
            }
        
        return {
            "response": """I'm the QA & Tester Agent. I can audit any URL for:
- 🐛 **Bugs**: Console errors, broken links
- ♿ **Accessibility**: Alt text, ARIA labels, form labels
- 🎨 **UX Quality**: Layout, clarity, user flow
- ⚡ **Performance**: Load time analysis

Provide a URL and I'll run a full audit!""",
            "agent": "qa_tester",
        }
    
    async def close(self):
        """Cleanup browser resources"""
        if self._browser:
            await self._browser.close()
            self._browser = None
            logger.info("QA Browser closed")


# Singleton instance
qa_tester_agent = QATesterAgent()
