"""
Voice Agents API
Powered by Qwen-TTS
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.voice import voice_service

router = APIRouter()

class SpeakRequest(BaseModel):
    text: str
    voice_id: Optional[str] = "qwen-tts-voice-design"
    model: Optional[str] = "cosyvoice-v1"

@router.post("/speak")
async def speak_text(
    request: SpeakRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate audio from text using Qwen-TTS.
    Returns MP3 audio binary.
    """
    try:
        audio_content = await voice_service.synthesize(
            text=request.text,
            voice=request.voice_id,
            model=request.model
        )
        
        return Response(content=audio_content, media_type="audio/mpeg")
        
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice generation failed: {str(e)}")
