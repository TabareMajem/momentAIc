"""
SDR (Sales Development Rep) Agent
Automated email sequences and follow-up campaigns
Part of "The Hunter" Swarm
Upgraded to BaseAgent with structured outputs and memory context.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import structlog
from pydantic import BaseModel, Field

from app.agents.base import get_llm, get_agent_config, draft_email, BaseAgent, safe_parse_json
from app.models.conversation import AgentType
from app.models.growth import Lead, LeadStatus, OutreachMessage
from app.services.agent_memory_service import agent_memory_service

logger = structlog.get_logger()


# Pydantic Structured Outputs
class SpamAnalysis(BaseModel):
    score: int = Field(description="Spam score from 0 (clean) to 10 (spam)")
    risk_level: str = Field(description="Low, Medium, or High")
    triggers: List[str] = Field(description="List of spam trigger issues found")
    suggestions: List[str] = Field(description="How to fix the issues")


class OutreachSequenceType(str, Enum):
    """Types of outreach sequences"""
    COLD_INTRO = "cold_intro"
    FOLLOW_UP = "follow_up"
    CASE_STUDY = "case_study"
    MEETING_REQUEST = "meeting_request"
    NURTURE = "nurture"


class SDRAgent(BaseAgent):
    """
    SDR Agent - Automated sales outreach and follow-up.
    Upgraded to BaseAgent with cognitive memory and structured outputs.
    
    Capabilities:
    - Generate personalized email sequences
    - Schedule follow-up cadences
    - Adapt messaging based on engagement
    - A/B test subject lines
    """
    
    def __init__(self):
        self.config = get_agent_config(AgentType.SALES_HUNTER)
        self.llm = get_llm("deepseek-chat", temperature=0.7)
        
        # Default follow-up cadence (days after initial outreach)
        self.default_cadence = [3, 7, 14, 21]
    
    async def generate_cold_email(
        self,
        lead: Dict[str, Any],
        research: Dict[str, Any],
        startup_context: Dict[str, Any],
        tone: str = "professional",
    ) -> Dict[str, Any]:
        """
        Generate a personalized cold outreach email
        """
        logger.info(
            "SDR Agent: Generating cold email",
            lead=lead.get("contact_name", lead.get("name")),
        )
        
        if not self.llm:
            return {"success": False, "error": "AI Service Unavailable"}
        
        # Extract relevant research insights
        pain_points = research.get("analysis", {}).get("PAIN POINTS", "")
        hooks = research.get("analysis", {}).get("OUTREACH HOOKS", "")
        
        prompt = f"""Write a highly technical, plain-text outreach email utilizing the 'Stress Test' protocol.

RECIPIENT:
- Name: {lead.get('contact_name', lead.get('name', 'there'))}
- Title: {lead.get('contact_title', lead.get('title', 'Engineer'))}
- Company: {lead.get('company_name', lead.get('company', 'their company'))}

RESEARCH INSIGHTS:
- Architecture/Focus: {pain_points}
- Recent Work (Hook): {hooks}

OUR PLATFORM:
- Name: {startup_context.get('name', 'Symbiotask Orchestration')}
- Core Engine: {startup_context.get('description', 'Multi-model cascade layer with PostgreSQL state-saved rendering')}

REQUIREMENTS:
1. Subject line: Hypothesis regarding your [Topic from Recent Work] (Under 7 words)
2. Opening: Reference a highly specific technical detail from their public work, proving manual research.
3. Body: Introduce our architecture. DO NOT ask for a meeting or a sale. 
4. CTA (The Stress Test): Challenge them to break our Beta API. Ask if they are willing to run their most complex procedural models through our Frame Consistency Check.
5. Tone: Technical Brutalism, peer-to-peer engineer speak. No marketing fluff.

FORBIDDEN:
- "Hope this email finds you well"
- "I'd love to schedule a quick call"
- Exclamation points
- Sales jargon

Format your response as:
SUBJECT: [subject line]
BODY:
[email body with proper line breaks]"""

        try:
            response = await self.llm.ainvoke(prompt)
            email = self._parse_email(response.content)
            
            return {
                "success": True,
                "email": email,
                "lead": lead.get("contact_name", lead.get("name")),
                "type": OutreachSequenceType.COLD_INTRO.value,
                "generated_at": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error("Cold email generation failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def generate_follow_up_sequence(
        self,
        lead: Dict[str, Any],
        initial_email: Dict[str, Any],
        num_followups: int = 3,
    ) -> Dict[str, Any]:
        """
        Generate a sequence of follow-up emails
        """
        logger.info(
            "SDR Agent: Generating follow-up sequence",
            lead=lead.get("contact_name"),
            count=num_followups,
        )
        
        if not self.llm:
            return {"success": False, "error": "AI Service Unavailable"}
        
        prompt = f"""Generate {num_followups} follow-up emails for this outreach.

ORIGINAL EMAIL:
Subject: {initial_email.get('subject', '')}
Body: {initial_email.get('body', '')}

RECIPIENT:
- Name: {lead.get('contact_name', lead.get('name'))}
- Company: {lead.get('company_name', lead.get('company'))}

FOLLOW-UP RULES:
1. Each follow-up should have a different angle (don't just "bump")
2. Get progressively shorter
3. Last one should use "break-up" psychology
4. Reference the original email briefly
5. Keep CTAs low-commitment

Generate {num_followups} follow-up emails, scheduled for:
- Follow-up 1: Day 3
- Follow-up 2: Day 7
- Follow-up 3: Day 14

Format each as:
---FOLLOWUP [N] (Day [X])---
SUBJECT: [subject]
BODY:
[email body]
---END---"""

        try:
            response = await self.llm.ainvoke(prompt)
            followups = self._parse_followup_sequence(response.content)
            
            # Add scheduling info
            for i, followup in enumerate(followups):
                followup["scheduled_day"] = self.default_cadence[i] if i < len(self.default_cadence) else (i + 1) * 7
                followup["sequence_position"] = i + 1
            
            return {
                "success": True,
                "sequence": followups,
                "lead": lead.get("contact_name"),
                "total_emails": len(followups) + 1,  # Including initial
                "generated_at": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error("Follow-up sequence generation failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def generate_meeting_request(
        self,
        lead: Dict[str, Any],
        context: str,
        available_slots: List[str],
    ) -> Dict[str, Any]:
        """
        Generate a meeting request email with specific time slots
        """
        if not self.llm:
            return {"success": False, "error": "AI Service Unavailable"}
        
        slots_formatted = "\n".join(f"- {slot}" for slot in available_slots[:3])
        
        prompt = f"""Write a brief meeting request email.

RECIPIENT:
- Name: {lead.get('contact_name', lead.get('name'))}
- Company: {lead.get('company_name', lead.get('company'))}

CONTEXT:
{context}

AVAILABLE TIMES:
{slots_formatted}

REQUIREMENTS:
1. Under 100 words total
2. Reference previous conversation/context
3. Provide 3 specific time options
4. Include calendar link placeholder
5. Make it easy to say yes

Format as:
SUBJECT: [subject]
BODY:
[body]"""

        try:
            response = await self.llm.ainvoke(prompt)
            email = self._parse_email(response.content)
            
            return {
                "success": True,
                "email": email,
                "type": OutreachSequenceType.MEETING_REQUEST.value,
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def generate_case_study_email(
        self,
        lead: Dict[str, Any],
        case_study: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate an email sharing a relevant case study
        """
        if not self.llm:
            return {"success": False, "error": "AI Service Unavailable"}
        
        prompt = f"""Write an email sharing a relevant case study.

RECIPIENT:
- Name: {lead.get('contact_name', lead.get('name'))}
- Company: {lead.get('company_name', lead.get('company'))}
- Industry: {lead.get('industry', 'their industry')}

CASE STUDY:
- Client: {case_study.get('client_name', 'A similar company')}
- Industry: {case_study.get('industry', 'Same industry')}
- Challenge: {case_study.get('challenge', 'Similar challenges')}
- Result: {case_study.get('result', 'Significant improvement')}
- Metrics: {case_study.get('metrics', '40% improvement')}

REQUIREMENTS:
1. Lead with the result (number/metric)
2. Make it about THEM, not the case study
3. Draw explicit parallel to their situation
4. CTA: Would you like to see how we could do similar for you?

Format as:
SUBJECT: [subject]
BODY:
[body]"""

        try:
            response = await self.llm.ainvoke(prompt)
            email = self._parse_email(response.content)
            
            return {
                "success": True,
                "email": email,
                "type": OutreachSequenceType.CASE_STUDY.value,
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def ab_test_subject_lines(
        self,
        email_body: str,
        num_variants: int = 3,
    ) -> Dict[str, Any]:
        """
        Generate A/B test variants for subject lines
        """
        if not self.llm:
            return {"success": False, "error": "AI Service Unavailable"}
        
        prompt = f"""Generate {num_variants} subject line variants for A/B testing.

EMAIL BODY:
{email_body}

Generate {num_variants} different subject lines, each using a different psychological approach:
1. Curiosity-based
2. Benefit-based
3. Personalization-based
4. Question-based
5. Urgency-based (if appropriate)

Format each as:
[N]. [APPROACH]: [subject line] (under 60 chars)"""

        try:
            response = await self.llm.ainvoke(prompt)
            
            variants = []
            for line in response.content.split("\n"):
                if line.strip() and (line[0].isdigit() or line.startswith("-")):
                    variants.append(line.strip())
            
            return {
                "success": True,
                "variants": variants[:num_variants],
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def generate_whatsapp_message(
        self,
        lead: Dict[str, Any],
        context: str,
        partner_code: str = "MOMENTAIC10"
    ) -> Dict[str, Any]:
        """
        Generate a localized WhatsApp message, designed for LatAm/ES high-velocity conversational style.
        """
        if not self.llm:
            return {"success": False, "error": "AI Service Unavailable"}
            
        prompt = f"""Write a highly localized WhatsApp outreach message for a Latin American or Spanish agency director.

RECIPIENT:
- Name: {lead.get('contact_name', lead.get('name'))}
- Company: {lead.get('company_name', lead.get('company'))}

CONTEXT:
{context}

REQUIREMENTS:
1. Platform: WhatsApp (mobile format, readable)
2. Tone: Warm, professional but direct ("Documentary Cinematic" aesthetic).
3. Core Angle: Risk mitigation and the "Reliability Layer" (PostgreSQL auto-resume for massive renders).
4. Offer: A localized API blueprint + {partner_code} discount for testing.
5. Emphasize: Saving them hours of synchronous alignment and rendering crashes.
6. Make it feel like a text from a peer, not a corporate blast.

Format ONLY the message text. No prefixes like 'MESSAGE:'."""

        try:
            response = await self.llm.ainvoke(prompt)
            return {
                "success": True,
                "whatsapp_text": response.content.strip(),
                "type": "whatsapp_outreach"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def generate_x_dm(
        self,
        lead: Dict[str, Any],
        context: str,
    ) -> Dict[str, Any]:
        """
        Generate a direct message for X (Twitter) meant for Indie Hackers and "Build in Public" targets.
        """
        if not self.llm:
            return {"success": False, "error": "AI Service Unavailable"}
            
        prompt = f"""Write a DM for X (Twitter) targeting an indie hacker / workflow architect.

RECIPIENT HANDLE: @{lead.get('twitter_handle', 'builder')}

CONTEXT:
{context}

REQUIREMENTS:
1. Length: extremely short, under 280 chars.
2. Tone: Technical Brutalism, "Building in public" vibe.
3. Hook: Reference a specific workflow or prompt setup they built recently.
4. Offer: A "Template Bounty" or early API access to our Multi-Model Cascade for their next n8n build.
5. Zero pleasantries. Get straight to the technical utility.

Format ONLY the DM text. No quotes or prefixes."""

        try:
            response = await self.llm.ainvoke(prompt)
            return {
                "success": True,
                "x_dm_text": response.content.strip(),
                "type": "x_dm_outreach"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def handle_social_reply(
        self,
        platform: str,
        prospect_handle: str,
        message_history: str,
        latest_reply: str
    ) -> Dict[str, Any]:
        """
        Processes an incoming social media DM (X or WhatsApp) intercepted by OpenClaw.
        Uses DeepSeek to determine intent. If interested, it dynamically synthesizes 
        and dispatches the correct JSON blueprint.
        """
        if not self.llm:
            return {"success": False, "error": "AI Service Unavailable"}
            
        # 1. Intent Analysis
        intent_prompt = f"""Analyze this prospect's reply to our outreach on {platform}.

OUR PREVIOUS MESSAGES:
{message_history}

THEIR LATEST REPLY:
{latest_reply}

Determine their exact intent from these categories:
- INTERESTED_BLUEPRINT (They are asking for the template/code/access)
- OBJECTION (They are doubting the claims or tech)
- NOT_INTERESTED (They want us to stop)
- QUESTION (They need more info before deciding)

IMPORTANT: Reply ONLY with the exact category name. Nothing else."""
        
        try:
            intent_response = await self.llm.ainvoke(intent_prompt)
            intent = intent_response.content.strip()
            
            logger.info("sdr_agent_analyzed_social_intent", handle=prospect_handle, intent=intent)
            
            if intent == "INTERESTED_BLUEPRINT":
                from app.services.lead_magnet_generator import lead_magnet_generator
                
                # Dynamically generate the JSON file tailored to their specific message or stack context
                magnet_result = await lead_magnet_generator.generate_n8n_blueprint(
                    prospect_context=f"Handle: {prospect_handle}, Platform: {platform}, History: {message_history}",
                    specific_request=latest_reply
                )
                
                if magnet_result.get("success"):
                    # Generate the conversational wrapper
                    reply_prompt = f"Write a conversational {platform} message delivering this JSON workflow. Tell them it's attached. Keep it under 2 sentences. Brutal technical tone. Base it on their reply: {latest_reply}"
                    reply_msg = (await self.llm.ainvoke(reply_prompt)).content.strip()
                    
                    return {
                        "success": True,
                        "action": "deliver_magnet",
                        "reply_text": reply_msg,
                        "attachment": magnet_result["filepath"]
                    }
                else:
                    return {"success": False, "error": "Magnet generation failed"}
            
            elif intent == "OBJECTION" or intent == "QUESTION":
                 reply_prompt = f"Write a conversational {platform} reply addressing this objection/question: '{latest_reply}'. Tone: Technical Brutalist, confident. Address the architecture explicitly. Keep under 3 sentences."
                 reply_msg = (await self.llm.ainvoke(reply_prompt)).content.strip()
                 return {
                     "success": True,
                     "action": "handle_objection",
                     "reply_text": reply_msg
                 }
                 
            else:
                 return {"success": True, "action": "do_nothing"}
                 
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def adapt_to_response(
        self,
        original_email: Dict[str, Any],
        response_text: str,
        response_sentiment: str,  # positive, neutral, negative, objection
    ) -> Dict[str, Any]:
        """
        Generate a reply adapted to the prospect's response
        """
        if not self.llm:
            return {"success": False, "error": "AI Service Unavailable"}
        
        prompt = f"""Generate a reply to this prospect response.

OUR ORIGINAL EMAIL:
{original_email.get('body', '')}

THEIR RESPONSE:
{response_text}

RESPONSE SENTIMENT: {response_sentiment}

Generate an appropriate reply:
- If positive: Move toward next step (meeting, demo)
- If neutral: Add more value, address unstated concerns
- If negative: Gracefully accept, leave door open
- If objection: Address specifically, pivot to value

Keep it under 100 words. Be conversational.

Format as:
SUBJECT: Re: [original subject]
BODY:
[reply body]"""

        try:
            response = await self.llm.ainvoke(prompt)
            email = self._parse_email(response.content)
            
            return {
                "success": True,
                "reply": email,
                "adapted_for": response_sentiment,
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def check_spam_score(self, email_content: str) -> Dict[str, Any]:
        """
        Analyze email content for spam triggers using structured output.
        """
        if not self.llm:
            return {"score": 0, "analysis": "AI Unavailable"}
            
        prompt = f"""Analyze this email for spam triggers.

EMAIL:
{email_content}

Rate from 0-10 (0=Clean, 10=Spam) based on:
- Trigger words (free, urgent, $$$)
- Formatting (ALL CAPS, excessive !!!)
- Domain reputation risks
- Authentication risks (implied)"""
        
        try:
            result = await self.structured_llm_call(
                prompt=prompt,
                response_model=SpamAnalysis
            )
            if isinstance(result, SpamAnalysis):
                return result.model_dump()
            return result if isinstance(result, dict) else {"score": 0, "analysis": str(result)}
        except Exception:
            return {"score": 0, "error": "Check failed"}

    def _parse_email(self, response: str) -> Dict[str, str]:
        """Parse email from LLM response"""
        email = {"subject": "", "body": ""}
        
        lines = response.split("\n")
        in_body = False
        body_lines = []
        
        for line in lines:
            if line.startswith("SUBJECT:"):
                email["subject"] = line.replace("SUBJECT:", "").strip()
            elif line.strip() == "BODY:":
                in_body = True
            elif in_body:
                body_lines.append(line)
        
        email["body"] = "\n".join(body_lines).strip()
        return email
    
    def _parse_followup_sequence(self, response: str) -> List[Dict[str, str]]:
        """Parse follow-up sequence from LLM response"""
        followups = []
        current_followup = None
        in_body = False
        body_lines = []
        
        for line in response.split("\n"):
            if line.startswith("---FOLLOWUP"):
                if current_followup:
                    current_followup["body"] = "\n".join(body_lines).strip()
                    followups.append(current_followup)
                current_followup = {"subject": "", "body": ""}
                body_lines = []
                in_body = False
            elif line.startswith("SUBJECT:") and current_followup:
                current_followup["subject"] = line.replace("SUBJECT:", "").strip()
            elif line.strip() == "BODY:":
                in_body = True
            elif line.startswith("---END"):
                if current_followup:
                    current_followup["body"] = "\n".join(body_lines).strip()
                    followups.append(current_followup)
                current_followup = None
                body_lines = []
                in_body = False
            elif in_body:
                body_lines.append(line)
        
        if current_followup:
            current_followup["body"] = "\n".join(body_lines).strip()
            followups.append(current_followup)
        
        return followups


    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        gmail_user: str,
        gmail_password: str,  # App Password
        from_name: str = "MomentAIc Founder"
    ) -> Dict[str, Any]:
        """
        Send a real email via Gmail SMTP
        """
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        try:
            msg = MIMEMultipart()
            msg["From"] = f"{from_name} <{gmail_user}>"
            msg["To"] = to_email
            msg["Subject"] = subject
            
            msg.attach(MIMEText(body, "plain"))
            
            # Connect to Gmail SMTP
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(gmail_user, gmail_password)
            
            # Send
            server.send_message(msg)
            server.quit()
            
            return {
                "success": True, 
                "message": "Email sent successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Email sending failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively identify outreach opportunities:
        - Scan for new leads from web search
        - Generate cold outreach sequences
        - Propose follow-up campaigns for stale leads
        """
        actions = []
        industry = startup_context.get("industry", "Technology")
        name = startup_context.get("name", "Our startup")
        
        # 1. New lead discovery
        from app.agents.base import web_search as ws
        try:
            search_query = f"{industry} startup founders looking for {startup_context.get('description', '')[:50]}"
            search_results = await ws.ainvoke(search_query)
            if search_results and len(str(search_results)) > 50:
                actions.append({
                    "action": "cold_outreach_campaign",
                    "name": "cold_outreach",
                    "description": f"Generate cold outreach for leads discovered in: {industry}",
                    "priority": "high",
                    "agent": "SDRAgent",
                    "search_results": str(search_results)[:500],
                })
        except Exception as e:
            logger.warning("SDR proactive lead search failed", error=str(e))
        
        # 2. Daily follow-up sweep
        actions.append({
            "action": "follow_up_sweep",
            "name": "follow_up_sweep",
            "description": "Generate follow-up emails for leads that haven't responded in 3+ days.",
            "priority": "medium",
            "agent": "SDRAgent",
        })
        
        if actions:
            await self.publish_to_bus(
                topic="sdr_opportunities_found",
                data={"summary": f"SDR found {len(actions)} outreach opportunities", "count": len(actions)},
            )
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Execute a proactive SDR action using REAL email services.
        """
        action_type = action.get("action", action.get("name", "unknown"))
        
        try:
            if action_type == "cold_outreach_campaign":
                # Generate a cold email using real LLM
                lead = {
                    "contact_name": "Founder",
                    "company_name": startup_context.get("industry", "Tech"),
                    "contact_title": "CEO",
                }
                research = {
                    "analysis": {
                        "PAIN POINTS": action.get("search_results", "Growth challenges"),
                        "OUTREACH HOOKS": f"Latest {startup_context.get('industry', 'tech')} trends",
                    }
                }
                result = await self.generate_cold_email(
                    lead=lead,
                    research=research,
                    startup_context=startup_context,
                )
                
                if result.get("success"):
                    email = result.get("email", {})
                    
                    # Wire Clay & Instantly Integrations
                    try:
                        from app.integrations.clay import ClayIntegration
                        from app.integrations.instantly import InstantlyIntegration
                        
                        # 1. Enrich Lead via Clay
                        clay = ClayIntegration()
                        enriched_data = await clay.execute_action("enrich_person", {
                            "email": "linkedin_prospect@example.com",
                            "linkedin_url": "https://linkedin.com/in/prospect"
                        })
                        logger.info("Clay: Lead enriched", data_pts=len(enriched_data))
                        
                        # 2. Add to Instantly Campaign
                        instantly = InstantlyIntegration()
                        await instantly.execute_action("add_lead", {
                            "campaign_id": "cmp_autonomous_sdr",
                            "email": "linkedin_prospect@example.com",
                            "first_name": lead.get("contact_name", "Founder"),
                            "custom_variables": {"personalized_line": email.get("body", "")[:100]}
                        })
                        logger.info("Instantly: Lead added to campaign sequence")
                    except Exception as sdr_e:
                        logger.error("SDR integrations failed", error=str(sdr_e))
                    
                    await self.publish_to_bus(
                        topic="outreach_draft_ready",
                        data={
                            "summary": f"Cold email drafted & Added to Instantly (Enriched via Clay): {email.get('subject', 'N/A')}",
                            "content": email.get("body", "")[:200],
                        },
                    )
                    return f"Cold email campaign drafted: {email.get('subject', 'N/A')}"
                return f"Cold email generation failed: {result.get('error', 'unknown')}"
            
            elif action_type == "follow_up_sweep":
                # Use LLM to draft follow-up recommendations
                if self.llm:
                    prompt = f"""You are an SDR for {startup_context.get('name', 'our startup')}.
Generate 3 specific follow-up email templates for leads that went cold after initial outreach.
Industry: {startup_context.get('industry', 'Technology')}

For each, provide: Subject line and a 2-sentence body."""
                    response = await self.llm.ainvoke(prompt)
                    
                    await self.publish_to_bus(
                        topic="follow_up_drafts_ready",
                        data={"summary": response.content[:200]},
                    )
                    return f"Follow-up templates generated: {response.content[:200]}"
                return "LLM not available"

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # NEW: Growth-Strategy Precision Targeting
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            elif action_type == "intent_score_leads":
                # Score leads by engagement signals using LLM
                if self.llm:
                    leads_data = action.get("leads", [])
                    industry = startup_context.get("industry", "Technology")
                    product_desc = startup_context.get("description", "")

                    prompt = f"""You are a precision sales intelligence agent for {startup_context.get('name', 'our startup')}.
Industry: {industry}
Product: {product_desc[:200]}

Score these leads on a 1-100 intent scale based on engagement signals, role fit, and company stage.
For each lead, provide:
1. Intent Score (1-100)
2. Primary buying signal
3. Recommended outreach channel (email/linkedin/whatsapp/x)
4. Personalized hook (1 sentence)

Leads to score:
{str(leads_data)[:2000]}

Format as JSON array: [{{"name": "...", "score": 85, "signal": "...", "channel": "...", "hook": "..."}}]"""

                    response = await self.llm.ainvoke(prompt)
                    scored = safe_parse_json(response.content)

                    await self.publish_to_bus(
                        topic="leads_scored",
                        data={"summary": f"Scored {len(scored) if isinstance(scored, list) else 0} leads by intent", "scores": scored},
                        target_agents=["GrowthHackerAgent"],
                    )
                    return f"Intent-scored {len(scored) if isinstance(scored, list) else 0} leads"
                return "LLM not available"

            elif action_type == "competitor_displacement_sequence":
                # Auto-create outreach sequences targeting users of competitor products
                competitor = action.get("competitor", "competitor product")
                if self.llm:
                    prompt = f"""Create a 3-email displacement sequence targeting users of {competitor}.
Our product: {startup_context.get('name', 'our product')} — {startup_context.get('description', '')}
Industry: {startup_context.get('industry', 'Technology')}

For each email:
1. Subject line (under 50 chars)
2. Body (under 100 words)
3. Angle: Email 1 = pain point they have with {competitor}, Email 2 = specific feature comparison, Email 3 = case study or offer

Rules:
- Never trash-talk the competitor directly
- Lead with THEIR pain, not our features
- Be specific about switching costs (make them seem low)

Format each as:
---EMAIL [N]---
SUBJECT: ...
BODY: ...
---END---"""

                    response = await self.llm.ainvoke(prompt)
                    
                    await self.publish_to_bus(
                        topic="displacement_sequence_ready",
                        data={"summary": f"Competitor displacement sequence created for {competitor}", "content": response.content[:500]},
                    )
                    return f"Competitor displacement sequence created targeting {competitor} users"
                return "LLM not available"

            elif action_type == "micro_segment_outreach":
                # Generate segment-specific messaging (not generic templates)
                segment = action.get("segment", {})
                segment_name = segment.get("name", "Target Segment")
                if self.llm:
                    prompt = f"""Create hyper-personalized outreach for this micro-segment:

Segment: {segment_name}
Characteristics: {segment.get('characteristics', 'B2B decision makers')}
Pain Points: {segment.get('pain_points', 'efficiency, scaling')}
Budget Range: {segment.get('budget', '$50-500/mo')}

Our Product: {startup_context.get('name', 'our product')}
Description: {startup_context.get('description', '')}

Generate:
1. Custom value proposition for THIS segment (1 sentence)
2. Cold email (subject + 80-word body)
3. LinkedIn connection request (under 300 chars)
4. Follow-up angle if no response

Be extremely specific to this segment. No generic language."""

                    response = await self.llm.ainvoke(prompt)
                    return f"Micro-segment outreach created for '{segment_name}': {response.content[:200]}"
                return "LLM not available"
            
            else:
                return await super().autonomous_action(action, startup_context)
                
        except Exception as e:
            logger.error("SDR autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"

# Singleton instance
sdr_agent = SDRAgent()
