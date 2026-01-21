from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_active_user
from app.models.user import User
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# Reuse Admin Guard
ADMIN_EMAIL = "tabaremajem@gmail.com"

def verify_god_mode(current_user: User = Depends(get_current_active_user)):
    if current_user.email.lower() != ADMIN_EMAIL.lower() and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="⛔ SWARM ACCESS DENIED."
        )
    return current_user

class DeployRequest(BaseModel):
    dry_run: bool = True  # Default to safe mode

@router.post("/deploy/{product_id}")
async def deploy_swarm(
    product_id: str, 
    request: Optional[DeployRequest] = None,
    admin: User = Depends(verify_god_mode)
):
    """
    UNLEASH THE SWARM.
    Triggers 10 parallel autonomous agents for the specified product.
    Set dry_run=False for LIVE FIRE mode.
    """
    from app.services.swarm_service import swarm_service
    
    dry_run = request.dry_run if request else True
    
    try:
        return await swarm_service.deploy_product_swarm(product_id, dry_run=dry_run)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
