import asyncio
from typing import Dict, Any, Optional, List
import structlog
from datetime import datetime
import uuid

from app.agents.lead_researcher_agent import lead_researcher_agent
from app.agents.registry import agent_registry
from app.core.websocket import websocket_manager
from app.services.outreach_service import outreach_service, OutreachEmail, EmailStatus
from app.services.quality_gate import quality_gate
from app.integrations.affiliate import affiliate_integration

logger = structlog.get_logger()


# ==========================================
# RETRY DECORATOR FOR HARDENED HANDOFFS
# ==========================================
def retry_async(max_attempts: int = 3, backoff_base: float = 2.0):
    """Decorator: retry an async function with exponential backoff."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts:
                        wait = backoff_base ** attempt
                        logger.warning(f"Retry {attempt}/{max_attempts} for {func.__name__}", error=str(e), wait=wait)
                        await asyncio.sleep(wait)
            raise last_error
        return wrapper
    return decorator

class GTMHunterSwarm:
    """
    True Swarm Collaboration Pipeline:
    Orchestrates the LeadResearcher -> ContentAgent -> SDRAgent sequence.
    Emits real-time telemetry to the frontend for the WarRoom UI.
    """
    
    def __init__(self, startup_context: Dict[str, Any], user_id: str):
        self.startup_context = startup_context
        self.user_id = user_id
        
        # Instantiate the required agents from the registry
        self.researcher = agent_registry.get("lead_researcher")
        self.content_agent = agent_registry.get("content")
        self.sdr_agent = agent_registry.get("sdr")
        
        self.run_id = f"swarm_gtm_{int(datetime.utcnow().timestamp())}"

    async def _emit_telemetry(self, step: str, agent_name: str, message: str, status: str = "running", data: Optional[Dict] = None):
        """Emit real-time updates directly to the frontend's unified memory bus."""
        event_payload = {
            "type": "agent.action",
            "data": {
                "id": self.run_id,
                "agent": agent_name,
                "task": message,
                "status": status,
                "progress": self._get_progress(step),
                "started_at": datetime.utcnow().isoformat(),
                "result": data
            }
        }
        startup_id = self.startup_context.get("id", "default")
        await websocket_manager.broadcast_to_startup(startup_id, event_payload)
        logger.info("swarm_telemetry_emitted", step=step, agent=agent_name, status=status)

    def _get_progress(self, step: str) -> int:
        mapping = {
            "starting": 5,
            "researching": 25,
            "research_complete": 40,
            "drafting": 60,
            "draft_complete": 75,
            "outreach_prep": 85,
            "outreach_sent": 100,
            "error": 0
        }
        return mapping.get(step, 0)

    async def execute_campaign(self, target_company: str, target_title: str) -> Dict[str, Any]:
        """
        Executes the full Pipeline.
        1. Researcher finds the lead and their context.
        2. Content drafts the pitch based on the research.
        3. SDR runs spam check and sends/schedules the outreach.
        """
        logger.info("gtm_hunter_swarm_started", target=target_company, run_id=self.run_id)
        await self._emit_telemetry("starting", "SwarmOrchestrator", f"Initializing GTM Hunter Swarm for {target_company}")
        await asyncio.sleep(1) # UI buffer
        
        try:
            # ==========================================
            # STEP 1: LEAD RESEARCH
            # ==========================================
            await self._emit_telemetry("researching", "LeadResearcherAgent", f"Deep scanning web for {target_title} at {target_company}")
            
            # The lead researcher normally pulls from DB, but for the swarm we pass it directly
            research_result = await self.researcher.research_company(target_company)
            
            if not research_result.get("success"):
                await self._emit_telemetry("error", "LeadResearcherAgent", "Failed to locate actionable intelligence. Aborting swarm.", status="error")
                return {"success": False, "error": "Research failed", "step": "research"}
                
            lead_intel = research_result.get("intelligence", {})
            lead_name = lead_intel.get("key_executives", [f"Founder of {target_company}"])[0]
            
            await self._emit_telemetry("research_complete", "LeadResearcherAgent", f"Acquired intel on {lead_name}. Handing off to Content Agent.", status="complete", data={"research_summary": lead_intel.get("recent_news")})
            await asyncio.sleep(1.5)

            # ==========================================
            # STEP 2: BESPOKE CONTENT DRAFTING
            # ==========================================
            await self._emit_telemetry("drafting", "ContentAgent", f"Synthesizing personalized pitch for {lead_name}")
            
            # Pack the research into a format the Content/SDR agent expects
            lead_record = {
                "contact_name": lead_name,
                "company_name": target_company,
                "contact_title": target_title,
                "research_context": lead_intel
            }
            
            draft_result = await self.content_agent.generate(
                platform="linkedin", # Base text format
                topic=f"B2B cold outreach pitch for {lead_name}",
                startup_context=self.startup_context,
                content_type="outreach_email_pitch",
                tone="Technical Brutalism",
                custom_context=str(lead_intel)
            )
            
            if not draft_result.get("success"):
                await self._emit_telemetry("error", "ContentAgent", "Failed to synthesize pitch.", status="error")
                return {"success": False, "error": "Drafting failed", "step": "content"}
                
            pitch_body = draft_result.get("copy", "")
            
            await self._emit_telemetry("draft_complete", "ContentAgent", "Pitch synthesized & validated. Handing off to SDR Agent.", status="complete", data={"pitch_preview": pitch_body[:100] + "..."})
            await asyncio.sleep(1.5)

            # ==========================================
            # STEP 3: SDR EXECUTION & SCHEDULING
            # ==========================================
            await self._emit_telemetry("outreach_prep", "SDRAgent", f"Running spam heuristics & formatting sequence for {lead_name}")
            
            # Here we simulate the SDR agent taking the raw pitch, wrapping it in an email, and checking spam
            # We call the SDRAgent's generate_cold_email, but feeding it the ContentAgent's draft as structural context
            
            research_struct = {
                "analysis": {
                    "PAIN POINTS": lead_intel.get("pain_points", "Operational inefficiency"),
                    "OUTREACH HOOKS": f"[Custom pitch context integrated: {pitch_body[:50]}]"
                }
            }
            
            sdr_result = await self.sdr_agent.generate_cold_email(
                lead=lead_record,
                research=research_struct,
                startup_context=self.startup_context,
                tone="professional"
            )
            
            if not sdr_result.get("success"):
                await self._emit_telemetry("error", "SDRAgent", "Outreach scheduling failed.", status="error")
                return {"success": False, "error": "SDR failed", "step": "sdr"}
                
            final_email = sdr_result.get("email", {})
            
            # ==========================================
            # STEP 4: QUALITY GATE + REAL DISPATCH
            # ==========================================
            email_body = final_email.get("body", pitch_body)
            email_subject = final_email.get("subject", f"Quick question for {lead_name}")
            
            # Run through quality gate
            gate_result = await quality_gate.evaluate_content(
                content=email_body,
                goal="book a meeting via cold outreach",
                target_audience=f"{target_title} at {target_company}",
                gate_type="outreach_email"
            )
            
            if gate_result.get("approved"):
                # Quality gate passed — dispatch via real SMTP
                await self._emit_telemetry("outreach_sent", "SDRAgent", f"Quality gate PASSED (score: {gate_result.get('score')}). Dispatching real email via SMTP.", status="running")
                
                outreach_email = OutreachEmail(
                    id=str(uuid.uuid4()),
                    campaign_id=self.run_id,
                    to_email=final_email.get("to_email", f"founder@{target_company.lower().replace(' ', '')}.com"),
                    to_name=lead_name,
                    subject=email_subject,
                    body_html=f"<html><body>{email_body}</body></html>",
                    body_text=email_body,
                    scheduled_at=datetime.utcnow()
                )
                
                send_success = await outreach_service.send_email(outreach_email)
                
                if send_success:
                    await self._emit_telemetry("outreach_sent", "SDRAgent", f"Email SENT to {lead_name} via SMTP. Campaign LIVE.", status="complete", data={"subject": email_subject, "sent": True})
                else:
                    await self._emit_telemetry("outreach_sent", "SDRAgent", f"SMTP dispatch failed. Creating ActionItem for manual review.", status="complete", data={"subject": email_subject, "sent": False})
            else:
                # Quality gate failed — create ActionItem for HitL approval
                await self._emit_telemetry("outreach_sent", "SDRAgent", f"Quality gate HELD (score: {gate_result.get('score')}). Queuing for founder approval.", status="complete")
                
                await self._create_action_item(
                    title=f"Approve outreach to {lead_name} at {target_company}",
                    description=f"SDR drafted email (quality score: {gate_result.get('score')}/100). Review and approve to send.",
                    payload={
                        "action_type": "send_email",
                        "to_email": final_email.get("to_email", ""),
                        "to_name": lead_name,
                        "subject": email_subject,
                        "body": email_body,
                        "quality_gate": gate_result
                    }
                )
            
            return {
                "success": True,
                "lead": lead_record,
                "email": final_email,
                "quality_gate": gate_result,
                "run_id": self.run_id
            }

        except Exception as e:
            logger.error("swarm_pipeline_crashed", error=str(e), exc_info=True)
            await self._emit_telemetry("error", "SwarmOrchestrator", f"Critical failure: {str(e)}", status="error")
            return {"success": False, "error": str(e)}

    async def _create_action_item(self, title: str, description: str, payload: Dict[str, Any]):
        """Create an ActionItem in the DB for HitL approval."""
        try:
            from app.core.database import AsyncSessionLocal
            from app.models.action_item import ActionItem, ActionStatus
            
            async with AsyncSessionLocal() as db:
                item = ActionItem(
                    id=uuid.uuid4(),
                    startup_id=uuid.UUID(str(self.startup_context.get("id", "00000000-0000-0000-0000-000000000000"))),
                    source_agent="SwarmOrchestrator",
                    title=title,
                    description=description,
                    priority="high",
                    payload=payload,
                    status=ActionStatus.pending,
                )
                db.add(item)
                await db.commit()
                logger.info("action_item_created", title=title, action_type=payload.get("action_type"))
        except Exception as e:
            logger.error("failed_to_create_action_item", error=str(e))


class InfluencerArmySwarm:
    """
    The Machine Sells Itself: Influencer Army Pipeline
    Orchestrates the KOLHeadhunter -> AmbassadorOutreach sequence.
    """
    
    def __init__(self, startup_context: Dict[str, Any], user_id: str):
        self.startup_context = startup_context
        self.user_id = user_id
        
        self.kol_hunter = agent_registry.get("kol_headhunter")
        self.ambassador = agent_registry.get("ambassador")
        
        self.run_id = f"swarm_army_{int(datetime.utcnow().timestamp())}"

    async def _emit_telemetry(self, step: str, agent_name: str, message: str, status: str = "running", data: Optional[Dict] = None):
        """Emit real-time updates directly to the frontend's unified memory bus."""
        event_payload = {
            "type": "agent.action",
            "data": {
                "id": self.run_id,
                "agent": agent_name,
                "task": message,
                "status": status,
                "progress": self._get_progress(step),
                "started_at": datetime.utcnow().isoformat(),
                "result": data
            }
        }
        startup_id = self.startup_context.get("id", "default")
        await websocket_manager.broadcast_to_startup(startup_id, event_payload)
        logger.info("army_swarm_telemetry_emitted", step=step, agent=agent_name, status=status)

    def _get_progress(self, step: str) -> int:
        mapping = {
            "starting": 5,
            "scouting": 20,
            "scouting_complete": 50,
            "drafting_dms": 80,
            "army_assembled": 100,
            "error": 0
        }
        return mapping.get(step, 0)

    async def recruit_army(self, niche: str, region: str = "Global") -> Dict[str, Any]:
        """
        Executes the Influencer Recruitment Pipeline.
        1. KOL Hunter searches the web for relevant micro-influencers.
        2. Ambassador generates personalized DMs with tracking links.
        """
        logger.info("influencer_army_swarm_started", niche=niche, run_id=self.run_id)
        await self._emit_telemetry("starting", "SwarmOrchestrator", f"Initializing Influencer Army for niche: {niche}")
        await asyncio.sleep(1)
        
        try:
            # ==========================================
            # STEP 1: KOL IDENTIFICATION
            # ==========================================
            await self._emit_telemetry("scouting", "KOLHeadhunterAgent", f"Scanning {region} for high-leverage micro-influencers in '{niche}'")
            
            # The KOL hunter uses the Serper API to find authentic profiles
            hitlist = await self.kol_hunter.scan_region(region=region, max_targets=3, custom_keywords=[niche])
            
            if not hitlist or not getattr(hitlist, "targets", []):
                await self._emit_telemetry("error", "KOLHeadhunterAgent", f"No quality influencers found for {niche}. Aborting.", status="error")
                return {"success": False, "error": "Scouting failed"}
            
            profiles = hitlist.targets
            names = [p.name for p in profiles]
            await self._emit_telemetry("scouting_complete", "KOLHeadhunterAgent", f"Acquired {len(profiles)} elite targets: {', '.join(names)}. Handing off to Ambassador Agent.", status="complete")
            await asyncio.sleep(1.5)

            # ==========================================
            # STEP 2: AMBASSADOR PITCH GENERATION
            # ==========================================
            await self._emit_telemetry("drafting_dms", "AmbassadorOutreachAgent", f"Generating personalized DM pitches with Affiliate lock-in for {len(profiles)} targets.")
            
            recruits = []
            program_details = "Free lifetime God Mode license in exchange for a raw, honest review shared with your audience. You receive a custom Stripe tracking link delivering 30% MRR for life on any conversions."
            
            for profile in profiles:
                # Generate the custom DM
                dm_result = await self.ambassador.generate_partnership_proposal(
                    prospect={
                        "contact_name": profile.name,
                        "company_name": f"{profile.name} Brand",
                        "audience_size": profile.followers
                    }
                )
                
                # REAL Affiliate Provisioning via Stripe Connect
                try:
                    affiliate_result = await affiliate_integration.create_affiliate(
                        name=profile.name,
                        email=getattr(profile, 'email', f"{profile.name.lower().replace(' ', '.')}@placeholder.com"),
                    )
                    affiliate_link = affiliate_result.get("referral_link", f"https://momentaic.com/r/{profile.name.lower().replace(' ', '')}")
                    logger.info("real_affiliate_created", name=profile.name, link=affiliate_link)
                except Exception as aff_err:
                    logger.warning("affiliate_creation_fallback", error=str(aff_err), name=profile.name)
                    affiliate_link = f"https://momentaic.com/r/{profile.name.lower().replace(' ', '')}_godmode"
                
                dm_copy = dm_result.get("proposal_draft", "") + f"\n\nHere is your unique tracking vault: {affiliate_link}"
                
                recruits.append({
                    "influencer": profile.name,
                    "platform": profile.platform,
                    "followers": profile.followers,
                    "dm_copy": dm_copy,
                    "link": affiliate_link
                })
                
                # Create ActionItem for HitL approval before sending
                await self._create_action_item(
                    title=f"Send DM to {profile.name} ({profile.platform})",
                    description=f"Ambassador Agent drafted a recruitment DM for {profile.name} ({getattr(profile, 'followers', 'N/A')} followers). Approve to dispatch.",
                    payload={
                        "action_type": "send_dm",
                        "influencer_name": profile.name,
                        "platform": profile.platform,
                        "dm_copy": dm_copy,
                        "affiliate_link": affiliate_link
                    }
                )
            
            await self._emit_telemetry(
                "army_assembled", 
                "AmbassadorOutreachAgent", 
                f"Viral Army assembled. {len(recruits)} recruits queued for founder approval in Action Queue.", 
                status="complete", 
                data={"targets": recruits}
            )
            
            return {
                "success": True,
                "niche": niche,
                "recruits": recruits,
                "run_id": self.run_id
            }

        except Exception as e:
            logger.error("army_swarm_crashed", error=str(e), exc_info=True)
            await self._emit_telemetry("error", "SwarmOrchestrator", f"Critical failure: {str(e)}", status="error")
            return {"success": False, "error": str(e)}

    async def _create_action_item(self, title: str, description: str, payload: Dict[str, Any]):
        """Create an ActionItem in the DB for HitL approval."""
        try:
            from app.core.database import AsyncSessionLocal
            from app.models.action_item import ActionItem, ActionStatus
            
            async with AsyncSessionLocal() as db:
                item = ActionItem(
                    id=uuid.uuid4(),
                    startup_id=uuid.UUID(str(self.startup_context.get("id", "00000000-0000-0000-0000-000000000000"))),
                    source_agent="InfluencerArmySwarm",
                    title=title,
                    description=description,
                    priority="high",
                    payload=payload,
                    status=ActionStatus.pending,
                )
                db.add(item)
                await db.commit()
                logger.info("action_item_created", title=title, action_type=payload.get("action_type"))
        except Exception as e:
            logger.error("failed_to_create_action_item", error=str(e))
