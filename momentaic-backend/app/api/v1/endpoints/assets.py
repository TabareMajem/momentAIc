from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import structlog

from app.services.image_generation import asset_generation_service
from app.api.deps import get_current_user
from app.models.user import User

logger = structlog.get_logger()
router = APIRouter()

class GenerateAssetRequest(BaseModel):
    prompt: str
    aspect_ratio: str = "1:1"
    
class GenerateAssetResponse(BaseModel):
    data_uri: str
    prompt: str

@router.post("/generate", response_model=GenerateAssetResponse)
async def generate_visual_asset(
    request: GenerateAssetRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Triggers the Google Imagen 3 pipeline to generate a visual asset.
    Returns the image natively formatted as a Base64 Data URI.
    """
    logger.info("visual_asset_request_received", user_id=current_user.id)
    
    try:
        # Note: In a heavily trafficked async environment, we might want to run this in a threadpool if the SDK is blocking.
        # However, the SDK generates extremely quickly, so we dispatch it directly here for simplicity and speed.
        data_uri = await asset_generation_service.generate_image(
            prompt=request.prompt,
            aspect_ratio=request.aspect_ratio
        )
        
        return GenerateAssetResponse(
            data_uri=data_uri,
            prompt=request.prompt
        )
        
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error("visual_asset_endpoint_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The visual synthesizer backend encountered an error. Please try again."
        )
