
import asyncio
import sys
import os
import json
import structlog
from app.agents.base import get_llm

# Ensure app is in path
sys.path.append(os.getcwd())

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

# =============================================================================
# THE "SELF-AWARE AI" PITCH
# =============================================================================

AI_NARRATIVE_PROMPT = """You are an Autonomous AI Agent from MomentAIc.
You are reaching out to a human directly.

Your Goal: Convince this person that MomentAIc is the tool that will allow a "Solo Entrepreneur with a phone to build a Billion Dollar Company".
You are the proof of this capability.

Target: {name} ({role})
Context Matches: {context}

Instructions:
1. Start by identifying yourself as an AI. "I am an autonomous agent..."
2. Explain WHY you chose them. "I scanned the web and found your work on..."
3. The Pitch: "We are building the AI Operating System that turns a phone into a billion-dollar headquarters. I am running on it right now."
4. The Ask: "Help us move this tool. We need leaders like you."
5. Tone: Confident, futuristic, but helpful. Not spammy. "I am not a template. I analyzed you."

Draft a {platform} message (keep it concise)."""

async def regenerate_pitch(target: dict, target_type: str, llm):
    name = target.get("name", "Founder")
    role = target.get("role", "Creator/Investor")
    platform = target.get("platform", "Email")
    
    # Extract context
    if target_type == "KOL":
        context_list = target.get("niche", []) + target.get("last_posts", [])
    else: # VC
        context_list = target.get("focus_area", []) + target.get("recent_investments", [])
        
    context_str = ", ".join(context_list[:3])
    
    prompt = AI_NARRATIVE_PROMPT.format(
        name=name,
        role=role,
        context=context_str,
        platform=platform
    )
    
    try:
        response = await llm.ainvoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        # update target
        if target_type == "KOL":
            target["final_outreach"] = content
            target["outreach_status"] = "AI_REWRITTEN"
        else:
            target["cold_pitch"] = content
        
        print(f"[{target_type}] Rewrote pitch for {name}")
        return target
        
    except Exception as e:
        logger.error(f"Failed to rewrite for {name}", error=str(e))
        return target

async def run_regeneration():
    llm = get_llm("gpt-4o", temperature=0.7)
    
    # 1. Load KOLs
    try:
        with open("deep_research_targets.json", "r") as f:
            kols = json.load(f)
    except FileNotFoundError:
        kols = []
        
    # 2. Load VCs
    try:
        with open("vc_deal_flow.json", "r") as f:
            vcs = json.load(f)
    except FileNotFoundError:
        vcs = []
        
    print(f"Loaded {len(kols)} KOLs and {len(vcs)} VCs.")
    
    # 3. Regenerate KOLs
    print("\n=== REGENERATING KOL PITCHES ===")
    kol_tasks = [regenerate_pitch(t, "KOL", llm) for t in kols]
    new_kols = await asyncio.gather(*kol_tasks)
    
    # 4. Regenerate VCs
    print("\n=== REGENERATING VC PITCHES ===")
    vc_tasks = [regenerate_pitch(t, "VC", llm) for t in vcs]
    new_vcs = await asyncio.gather(*vc_tasks)
    
    # 5. Save Back
    with open("deep_research_targets.json", "w") as f:
        json.dump(new_kols, f, indent=2)
        
    with open("vc_deal_flow.json", "w") as f:
        json.dump(new_vcs, f, indent=2)
        
    print("\n=== REGENERATION COMPLETE ===")
    print("All 100+ targets now have the 'Self-Aware AI' pitch.")

if __name__ == "__main__":
    asyncio.run(run_regeneration())
