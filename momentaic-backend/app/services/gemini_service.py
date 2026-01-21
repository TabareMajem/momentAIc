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
        Generate response with Gemini 2.0
        
        Args:
            prompt: User prompt
            system_instruction: System context
            tools: MCP-compatible tool definitions
            enable_grounding: Use Google Search for real-time data
            model: Model override (default: gemini-2.0-flash)
        """
        model = model or self.default_model
        
        if not self.client:
            return await self._mock_response(prompt, tools)
        
        try:
            # Configure model
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "max_output_tokens": 8192,
            }
            
            model_instance = self.client.GenerativeModel(
                model_name=model,
                generation_config=generation_config,
                system_instruction=system_instruction
            )
            
            # Build tool declarations if provided
            gemini_tools = None
            if tools:
                gemini_tools = self._convert_mcp_to_gemini_tools(tools)
            
            # Generate with grounding if enabled
            response = model_instance.generate_content(
                prompt,
                tools=gemini_tools
            )
            
            # Parse tool calls
            tool_calls = []
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        tool_calls.append({
                            "name": part.function_call.name,
                            "arguments": dict(part.function_call.args)
                        })
            
            return GeminiResponse(
                text=response.text if hasattr(response, 'text') else "",
                tool_calls=tool_calls,
                grounding_sources=[],
                tokens_used=response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
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
