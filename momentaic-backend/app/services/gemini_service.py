"""
Gemini 2.0 Integration
Latest Google DeepMind AI with native tool use, grounding, and multimodal capabilities
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json
import structlog

logger = structlog.get_logger()


@dataclass
class GeminiResponse:
    """Response from Gemini/AI model"""
    text: str
    tool_calls: List[Dict[str, Any]]
    grounding_sources: List[str]
    tokens_used: int
    model: str


class GeminiService:
    """
    Gemini 2.0 Flash integration with:
    - Native tool calling (MCP-compatible)
    - Google Search grounding
    - Deep Research mode
    - Multimodal (text + images + audio)
    - DeepSeek R1 Fallback
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.default_model = "gemini-2.0-flash"
        self.client = None
        self.deepseek_client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize Gemini client"""
        try:
            import google.generativeai as genai
            from app.core.config import settings
            
            api_key = self.api_key or getattr(settings, 'google_api_key', None)
            if api_key:
                genai.configure(api_key=api_key)
                self.client = genai
                logger.info("Gemini client initialized", model=self.default_model)
        except Exception as e:
            logger.warning("Gemini client init failed", error=str(e))

        # Initialize DeepSeek Fallback
        try:
            from app.core.config import settings
            if settings.deepseek_api_key:
                from openai import OpenAI
                self.deepseek_client = OpenAI(
                    api_key=settings.deepseek_api_key,
                    base_url="https://api.deepseek.com"
                )
                logger.info("DeepSeek client initialized (fallback)")
        except Exception as e:
            logger.warning("DeepSeek init failed", error=str(e))
    
    async def generate(
        self,
        prompt: str,
        system_instruction: str = None,
        tools: List[Dict] = None,
        enable_grounding: bool = False,
        model: str = None,
    ) -> GeminiResponse:
        """
        Generate response with Gemini 2.0 via REST API (to support custom headers)
        """
        import httpx
        from app.core.config import settings

        model = model or self.default_model
        api_key = self.api_key or getattr(settings, 'google_api_key', None)
        
        if not api_key:
            return await self._mock_response(prompt, tools)
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        headers = {
            "Content-Type": "application/json",
            "Referer": "https://momentaic.com",
            "X-Referer": "https://momentaic.com"
        }
        
        # Build Request Payload
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.95,
                "maxOutputTokens": 8192,
            }
        }

        if system_instruction:
            payload["system_instruction"] = {
                "parts": [{"text": system_instruction}]
            }

        # Tool Definitions
        if tools:
            function_declarations = []
            for tool in tools:
                function_declarations.append({
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool.get("input_schema", {})
                })
            payload["tools"] = [{"function_declarations": function_declarations}]
        
        if enable_grounding:
            # Add Google Search grounding if enabled
            if "tools" not in payload:
                payload["tools"] = []
            payload["tools"].append({"google_search_retrieval": {}})

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=60.0)
                
                if response.status_code != 200:
                    logger.error(f"Gemini API Error: {response.text}")
                    return await self._mock_response(prompt, tools)
                
                data = response.json()
                
                # Parse Response
                candidate = data.get("candidates", [{}])[0]
                content_parts = candidate.get("content", {}).get("parts", [])
                
                text_content = ""
                tool_calls = []
                grounding_sources = []
                
                for part in content_parts:
                    if "text" in part:
                        text_content += part["text"]
                    if "functionCall" in part:
                        tool_calls.append({
                            "name": part["functionCall"]["name"],
                            "arguments": part["functionCall"].get("args", {})
                        })
                
                # Extract grounding metadata if present
                if enable_grounding and "groundingMetadata" in candidate:
                    # Simplified extraction (structure varies)
                    pass

                usage = data.get("usageMetadata", {})
                
                return GeminiResponse(
                    text=text_content,
                    tool_calls=tool_calls,
                    grounding_sources=grounding_sources,
                    tokens_used=usage.get("totalTokenCount", 0),
                    model=model
                )

        except Exception as e:
            logger.error("Gemini generation failed", error=str(e))
            return await self._mock_response(prompt, tools)
    
    async def deep_research(
        self,
        topic: str,
        depth: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Deep Research mode - comprehensive web research
        
        Uses Gemini's Deep Research capability to:
        1. Formulate research plan
        2. Search multiple sources
        3. Synthesize findings
        4. Generate structured report
        """
        research_prompt = f"""
        Conduct deep research on: {topic}
        
        Research depth: {depth}
        
        Please:
        1. Identify key aspects to research
        2. Find authoritative sources
        3. Synthesize findings with citations
        4. Provide actionable insights for a startup founder
        
        Format as a structured research report.
        """
        
        response = await self.generate(
            prompt=research_prompt,
            system_instruction="You are a research assistant for startup founders. Provide comprehensive, actionable research.",
            enable_grounding=True
        )
        
        return {
            "topic": topic,
            "depth": depth,
            "report": response.text,
            "sources": response.grounding_sources,
            "model": response.model
        }
    
    async def browser_agent_task(
        self,
        task: str,
        url: str = None
    ) -> Dict[str, Any]:
        """
        Project Mariner-style browser agent task
        
        Performs web browsing tasks like:
        - Navigate and extract data
        - Fill forms
        - Click elements
        - Take screenshots
        """
        from app.agents.browser_agent import browser_agent
        
        result = await browser_agent.process(
            query=task,
            context={"start_url": url} if url else None
        )
        
        return {
            "task": task,
            "url": url,
            "result": result
        }
    
    async def generate_with_vision(
        self,
        prompt: str,
        image_path: str = None,
        image_url: str = None
    ) -> GeminiResponse:
        """
        Multimodal generation with image input
        """
        if not self.client:
            return await self._mock_response(prompt, None)
        
        try:
            import PIL.Image
            
            content = [prompt]
            
            if image_path:
                img = PIL.Image.open(image_path)
                content.append(img)
            
            model = self.client.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(content)
            
            return GeminiResponse(
                text=response.text,
                tool_calls=[],
                grounding_sources=[],
                tokens_used=0,
                model="gemini-2.0-flash"
            )
        except Exception as e:
            logger.error("Vision generation failed", error=str(e))
            return await self._mock_response(prompt, None)
    
    def _convert_mcp_to_gemini_tools(self, mcp_tools: List[Dict]) -> List:
        """Convert MCP tool format to Gemini function declarations"""
        try:
            from google.generativeai.types import FunctionDeclaration, Tool
            
            declarations = []
            for tool in mcp_tools:
                declarations.append(FunctionDeclaration(
                    name=tool["name"],
                    description=tool["description"],
                    parameters=tool.get("input_schema", {})
                ))
            
            return [Tool(function_declarations=declarations)]
        except Exception as e:
            logger.warning("Tool conversion failed", error=str(e))
            return None
    
    async def _mock_response(self, prompt: str, tools: List = None) -> GeminiResponse:
        """DeepSeek Fallback. Returns error if all providers fail."""
        # Try DeepSeek First
        if self.deepseek_client:
            try:
                response = self.deepseek_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant for a startup operating system called MomentAIc."},
                        {"role": "user", "content": prompt}
                    ],
                    stream=False
                )
                return GeminiResponse(
                    text=response.choices[0].message.content,
                    tool_calls=[],
                    grounding_sources=[],
                    tokens_used=response.usage.total_tokens,
                    model="deepseek-chat"
                )
            except Exception as e:
                logger.error("DeepSeek fallback failed", error=str(e))
        
        # [PHASE 25 FIX] No mock data - Return transparent error
        logger.error("All AI providers failed. Returning error to user.")
        return GeminiResponse(
            text="⚠️ **AI Service Temporarily Unavailable**\n\nWe couldn't process your request because our AI services are currently experiencing issues. This could be due to:\n- Missing or invalid API keys\n- Rate limiting\n- Temporary service outage\n\nPlease try again later or contact support if the issue persists.",
            tool_calls=[],
            grounding_sources=[],
            tokens_used=0,
            model="error"
        )


# Singleton
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get the Gemini service instance"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
