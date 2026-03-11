import json
import asyncio
import uuid
from typing import AsyncGenerator, Dict, Any, List

# In a real environment with the package installed:
# from src.client import DeerFlowClient
# But for now, we'll create a mock/wrapper that implements the exactly
# described interface from the bytedance/deer-flow documentation.

class MockDeerFlowEvent:
    def __init__(self, event_type: str, data: dict):
        self.type = event_type
        self.data = data

class DeerFlowClient:
    """
    Mock implementation of the Embedded Python Client from DeerFlow.
    Matches the schema documented in the repository.
    """
    def __init__(self):
        self.is_connected = True

    def chat(self, prompt: str, thread_id: str) -> dict:
        """Synchronous chat response"""
        return {"content": f"Mock response for thread {thread_id}", "summary": "Success"}

    async def stream(self, prompt: str, thread_id: str) -> AsyncGenerator[MockDeerFlowEvent, None]:
        """Streaming chat response (LangGraph SSE protocol)"""
        words = ["Analyzing", "startup", "data...", "Connecting", "to", "sandbox...", "Done."]
        for word in words:
            await asyncio.sleep(0.3)
            yield MockDeerFlowEvent(
                event_type="messages-tuple",
                data={"type": "ai", "content": word + " "}
            )

    def update_skill(self, skill_name: str, enabled: bool, content: str = None) -> dict:
        return {"success": True, "skill": skill_name}
    
    def get_thread_result(self, thread_id: str) -> dict:
        return {
            "grade": "A-",
            "summary": "Strong team, massive TAM, but execution risks in GTM.",
            "risks": ["High customer acquisition cost", "Strong incumbent competitors"],
            "opportunities": ["First mover in AI-driven niché", "Viral growth loops"],
            "comparable_deals": ["Anthropic Series A", "Perplexity Seed"],
            "recommended_action": "Proceed with due diligence."
        }

# Global instances mapped to use cases
client = DeerFlowClient()

async def run_deal_oracle(submission: dict) -> AsyncGenerator[str, None]:
    """Deal Oracle: Full-spectrum startup intelligence engine"""
    thread_id = f"oracle-{submission.get('id', uuid.uuid4())}"
    
    prompt = f"""
    [DEAL ORACLE] Analyze this startup submission with maximum depth.
    
    Company: {submission.get('name', 'Unknown')}
    Market: {submission.get('market', 'General')} 
    Ask: {submission.get('ask', 'N/A')}
    
    SPAWN PARALLEL SUB-AGENTS for:
    1. Founding team credibility (LinkedIn, GitHub)
    2. Market size validation
    3. Competitor landscape
    4. Red flags (SEC, news)
    5. Pattern match against memory
    """
    
    # We yield raw strings formatted as SSE data for FastAPIs EventSourceResponse
    async for event in client.stream(prompt, thread_id=thread_id):
        if event.type == "messages-tuple":
            yield json.dumps({"token": event.data.get("content", "")})
    
    # Finally yield the structured result
    final_result = client.get_thread_result(thread_id)
    yield json.dumps({"token": "\n\n", "final_result": final_result})

async def run_roast_engine(file_text: str, claims: List[str]) -> AsyncGenerator[str, None]:
    """Roast Engine: Brutal pitch deck destruction via web search facts"""
    thread_id = f"roast-{uuid.uuid4()}"
    
    prompt = f"""
    [ROAST ENGINE]
    Ingested deck claims: {claims}
    
    For each claim: web_search to find contradicting evidence.
    Run python script in sandbox to calculate bullshit score.
    Generate 7-point roast.
    """
    
    async for event in client.stream(prompt, thread_id=thread_id):
        if event.type == "messages-tuple":
            yield json.dumps({"token": event.data.get("content", "")})
            
async def run_marketing_campaign(goals: dict) -> AsyncGenerator[str, None]:
    """Execute massive marketing campaigns via Sub-Agents"""
    thread_id = f"marketing-{uuid.uuid4()}"
    
    prompt = f"""
    [GROWTH HACKER CMO]
    Goals: {goals}
    
    SPAWN PARALLEL SUB-AGENTS:
    1. TikTok script writer & video generator (Seedance 2.0 / Kling)
    2. X Space conversational script (Voice)
    3. Email blast sequence generator
    """
    
    async for event in client.stream(prompt, thread_id=thread_id):
        if event.type == "messages-tuple":
            yield json.dumps({"token": event.data.get("content", "")})
