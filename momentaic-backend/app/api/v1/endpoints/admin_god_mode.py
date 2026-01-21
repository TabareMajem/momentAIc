from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_active_user
from app.models.user import User
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()

# Admin Email Guard
ADMIN_EMAIL = "tabaremajem@gmail.com"

def verify_god_mode(current_user: User = Depends(get_current_active_user)):
    if current_user.email.lower() != ADMIN_EMAIL.lower() and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="⛔ GOD MODE ACCESS DENIED: Reality Distortion Field inactive for this user."
        )
    return current_user

class ContentRequest(BaseModel):
    product_name: str

@router.get("/products")
async def get_ecosystem_products(admin: User = Depends(verify_god_mode)):
    """Return the list of ecosystem products."""
    from app.agents.empire_strategist import empire_strategist
    return {"products": empire_strategist.products}

@router.post("/nano-bananas")
async def generate_content(request: ContentRequest, admin: User = Depends(verify_god_mode)):
    """Trigger the Nano Bananas Content Engine."""
    from app.agents.empire_strategist import empire_strategist
    return await empire_strategist.generate_nano_bananas_content(request.product_name)

@router.post("/surprise-me")
async def surprise_me(admin: User = Depends(verify_god_mode)):
    """Trigger the Synergistic GTM Strategy Agent."""
    from app.agents.empire_strategist import empire_strategist
    return await empire_strategist.surprise_me_strategy()
