"""
Voice Service
Powered by Qwen-TTS (Alibaba Cloud DashScope)
"""

import json
import httpx
import structlog
from app.core.config import settings

logger = structlog.get_logger()

class VoiceService:
    """
    Service for generating high-quality speech using Qwen-TTS.
    """
    
    API_URL = "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/generation"
    
    async def synthesize(self, text: str, voice: str = "qwen-tts-voice-design", model: str = "cosyvoice-v1") -> bytes:
        """
        Synthesize text to speech.
        
        Args:
            text: The text to speak
            voice: The voice ID (default: qwen-tts-voice-design for custom design or preset)
            model: The model version
            
        Returns:
            Binary audio data (mp3)
        """
        if not settings.DASHSCOPE_API_KEY:
            logger.error("VoiceService: No API Key found")
            raise ValueError("DASHSCOPE_API_KEY not configured")

        headers = {
            "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Qwen-TTS / CosyVoice payload structure
        # Documentation: https://www.alibabacloud.com/help/en/model-studio/user-guide/text-to-speech
        payload = {
            "model": model,
            "input": {
                "text": text
            },
            "parameters": {
                "text_type": "PlainText",
                "format": "mp3",
                "sample_rate": 48000
            }
        }
        
        # If using specific voice design parameters, they would go here.
        # For now, we use the standard model.
        
        try:
            async with httpx.AsyncClient() as client:
                logger.info("VoiceService: Sending request to DashScope", text_len=len(text))
                
                response = await client.post(self.API_URL, headers=headers, json=payload, timeout=30.0)
                
                if response.status_code != 200:
                    logger.error("VoiceService: API Error", status=response.status_code, body=response.text)
                    raise Exception(f"TTS API Error: {response.text}")
                
                # DashScope returns binary audio directly or JSON depending on header.
                # Usually for 'generation' endpoint it might be a JSON with a URL or binary.
                # Let's check Content-Type.
                content_type = response.headers.get("content-type", "")
                
                if "application/json" in content_type:
                     # If it returns JSON, it might contain an error or a URL
                    data = response.json()
                    if "output" in data and "audio_url" in data["output"]:
                        # Download the audio from the URL
                        audio_url = data["output"]["audio_url"]
                        audio_res = await client.get(audio_url)
                        return audio_res.content
                    elif "code" in data:
                        raise Exception(f"API Error Code: {data.get('code')} - {data.get('message')}")
                
                # Direct binary output? (Some endpoints stream)
                return response.content

        except Exception as e:
            logger.error("VoiceService: Synthesis failed", error=str(e))
            raise e

voice_service = VoiceService()
