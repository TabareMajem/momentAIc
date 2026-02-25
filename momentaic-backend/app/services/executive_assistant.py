import structlog
import asyncio
from datetime import datetime
from typing import Dict, Any, List

from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.base import get_llm
from app.services.mcp_client import mcp_service
from app.services.notification_service import notification_service
from app.core.config import settings

logger = structlog.get_logger()

class ExecutiveAssistantService:
    """
    The 'Proactive' Agent.
    Wakes up, checks all MCP resources (Calendar, Email, DB, Files),
    synthesizes a briefing, and emails the user.
    """
    
    def __init__(self):
        self.llm = None # Lazy load

    async def run_daily_briefing(self):
        """
        Main entry point for the scheduled task.
        """
        logger.info("ExecutiveAssistant: Starting daily briefing generation")
        
        try:
            # 1. Gather Data (Parallel execution where possible)
            # We need to handle potential failures gracefully if an MCP server is down
            
            calendar_data = await self._get_calendar_events()
            email_data = await self._get_unread_emails()
            business_pulse = await self._get_business_pulse()
            project_todos = await self._get_project_todos()
            
            # 2. Synthesize Report
            briefing = await self._synthesize_report(
                calendar=calendar_data,
                emails=email_data,
                pulse=business_pulse,
                todos=project_todos
            )
            
            # 3. Deliver
            # We need a user context. For now, we'll send to the SMTP_FROM_EMAIL or a hardcoded admin
            # In a real multi-user app, we'd iterate users. Here we assume single-player mode.
            await self._deliver_briefing(briefing)
            
            logger.info("ExecutiveAssistant: Briefing delivered successfully")
            
        except Exception as e:
            logger.error("ExecutiveAssistant: Failed to generate briefing", error=str(e))

    async def _get_calendar_events(self) -> str:
        try:
            # Check if 'google' server is available
            tools = await mcp_service.list_tools("google") # Will raise if not connected
            # Assume tool name is 'list_calendar_events'
            result = await mcp_service.call_tool("google", "list_calendar_events", {
                "max_results": 5
            })
            # result is a list of TextContent or similar. 
            # The MCP SDK returns a specific structure.
            # We'll convert to string.
            return str(result)
        except Exception as e:
            logger.warning("ExecutiveAssistant: Calendar check failed", error=str(e))
            return "Unable to access Calendar (Check MCP connection or API enablement)."

    async def _get_unread_emails(self) -> str:
        try:
            await mcp_service.list_tools("google")
            result = await mcp_service.call_tool("google", "list_gmail_messages", {
                "max_results": 5,
                "query": "is:unread category:primary"
            })
            return str(result)
        except Exception as e:
            logger.warning("ExecutiveAssistant: Email check failed", error=str(e))
            return "Unable to access Gmail."

    async def _get_business_pulse(self) -> str:
        """Query Postgres for key metrics"""
        try:
            # Check postgres
            await mcp_service.list_tools("postgres")
            
            # Simple query: Count recent users (just an example, schema depends on app)
            # We'll just list tables for now if we don't know schema, 
            # Or query 'users' table if standard.
            # Let's try a safe query.
            sql = "SELECT count(*) as user_count FROM users;"
            
            result = await mcp_service.call_tool("postgres", "query", {"sql": sql})
            return f"User Count: {result}"
        except Exception as e:
            logger.warning("ExecutiveAssistant: DB check failed", error=str(e))
            return "Unable to access Database (Postgres MCP unavailable)."

    async def _get_project_todos(self) -> str:
        """Read TODO.md from filesystem"""
        try:
            await mcp_service.list_tools("filesystem")
            
            # Try to read TODO.md or task.md
            # We know task.md exists in the brain, but maybe there is a root TODO?
            # Let's list the root dir and see if we find a likely file, or just read task.md from known path?
            # The filesystem server is rooted at PROJECT_ROOT.
            # Let's try to read 'README.md' as a fallback if TODO doesn't exist, just to show capability.
            # Or better, just say "Filesystem accessible".
            
            # Let's try to read 'task.md' if we know the path. 
            # But the path is dynamic /root/.gemini/...
            # We'll just list the root directory for "Recent Activity".
            
            result = await mcp_service.call_tool("filesystem", "list_directory", {"path": "."})
            return f"Project Root Files: {str(result)[:500]}..." 
        except Exception as e:
            logger.warning("ExecutiveAssistant: Filesystem check failed", error=str(e))
            return "Unable to access Filesystem."

    async def _synthesize_report(self, calendar, emails, pulse, todos) -> str:
        prompt = f"""
        You are an Executive Assistant AI for the Founder of MomentAIc.
        Synthesize a crisp, professional Morning Briefing based on the following real-time data data:

        📅 CALENDAR:
        {calendar}

        📧 EMAIL (Unread Primary):
        {emails}

        📊 BUSINESS PULSE (DB):
        {pulse}

        wd FILESYSTEM ACTIVITY:
        {todos}

        FORMAT:
        1. **Executive Summary** (1-2 sentences on state of the union)
        2. **Schedule & Focus** (Meeting highlights)
        3. **Inbox Zero Action Items** (Urgent emails only)
        4. **Business Health** (Metrics)
        
        Keep it concise. If data is missing/error, mention it briefly.
        """
        
        # Lazy load LLM to ensure it attaches to current event loop
        if not self.llm:
             self.llm = get_llm("gemini-2.5-flash", temperature=0.7)

        response = await self.llm.ainvoke([
            SystemMessage(content="You are a helpful, no-nonsense executive assistant."),
            HumanMessage(content=prompt)
        ])
        return response.content

    async def _deliver_briefing(self, content: str):
        """Send briefing via email, with file backup"""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        # Try email delivery first
        email_sent = False
        if settings.smtp_user:
            try:
                from app.services.email_service import get_email_service
                email_svc = get_email_service()
                
                # Convert markdown to basic HTML
                html_content = content.replace("\n", "<br>")
                html_body = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #6366f1;">☀️ Morning Briefing — {timestamp}</h1>
                    <div style="line-height: 1.6;">{html_content}</div>
                    <hr style="border: 1px solid #e5e7eb; margin: 20px 0;">
                    <p style="color: #9ca3af; font-size: 12px;">Generated by MomentAIc Executive Assistant</p>
                </div>
                """
                
                email_sent = await email_svc.send_email(
                    to_email=settings.smtp_from_email or settings.smtp_user,
                    subject=f"☀️ MomentAIc Morning Briefing — {timestamp}",
                    body=content,
                    html_body=html_body,
                )
                if email_sent:
                    logger.info("Briefing delivered via email")
            except Exception as e:
                logger.warning("Email delivery failed, falling back to file", error=str(e))
        
        # File backup (always write for auditability)
        filename = f"MORNING_BRIEF_{timestamp}.md"
        with open(filename, "w") as f:
            f.write(content)
        logger.info(f"Briefing saved to {filename}", email_sent=email_sent)

    async def check_urgent_comms(self):
        """
        Daemon-like check for 'Hair on Fire' issues (Server Down, Term Sheet, Angry Customer).
        Runs frequently (e.g. every 1-5 mins).
        """
        try:
            # Quick check for high-priority unread emails
            # We filter for specific keywords to avoid noise
            keywords = "subject:(URGENT OR 'Server Down' OR 'Term Sheet' OR 'Emergency')"
            
            # Use MCP to search
            # We assume 'google' tool is available
            tools = await mcp_service.list_tools("google")
            result = await mcp_service.call_tool("google", "list_gmail_messages", {
                "max_results": 3,
                "query": f"is:unread category:primary {keywords}"
            })
            
            # If we get a result string that isn't empty/brackets
            # The MCP returns text, let's parse or just check length
            res_str = str(result)
            
            if "threadId" in res_str or "snippet" in res_str:
                logger.warning("ExecutiveAssistant: 🔥 URGENT COMMS DETECTED 🔥")
                
                # Immediate Synthesis of the alert
                alert_msg = await self._synthesize_alert(res_str)
                
                # Dispatch Alert (File + Logs for now, SMS/Slack in future)
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"RED_ALERT_{timestamp}.md"
                with open(filename, "w") as f:
                    f.write(f"# 🚨 RED ALERT\n\n{alert_msg}")
                    
                logger.error(f"RED ALERT SAVED TO {filename}")
                
        except Exception as e:
            # info level to avoid spamming logs if just no connection
            logger.info("ExecutiveAssistant: Daemon check skipped (No connection)")

    async def _synthesize_alert(self, email_data) -> str:
        prompt = f"""
        🔥 HAIR ON FIRE ALERT 🔥
        
        Analyze these urgent emails:
        {email_data}
        
        Output a 1-sentence bottom line: WHAT IS BURNING?
        """
        if not self.llm:
             self.llm = get_llm("gemini-2.5-flash", temperature=0.5)

        response = await self.llm.ainvoke([
            SystemMessage(content="You are a crisis manager."),
            HumanMessage(content=prompt)
        ])
        return response.content


# Singleton
executive_assistant = ExecutiveAssistantService()
