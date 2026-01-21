from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_active_user
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()

# Reuse Admin Guard
ADMIN_EMAIL = "tabaremajem@gmail.com"

def verify_god_mode(current_user: User = Depends(get_current_active_user)):
    if current_user.email.lower() != ADMIN_EMAIL.lower() and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="⛔ NEXUS ACCESS DENIED."
        )
    return current_user

class FuseRequest(BaseModel):
    product_a: str
    product_b: str

@router.post("/fuse")
async def fuse_products(request: FuseRequest, admin: User = Depends(verify_god_mode)):
    """
    INITIATE NEXUS FUSION.
    Connects two products and generates a Synergy Protocol.
    """
    from app.services.nexus_service import nexus_service
    try:
        return await nexus_service.fuse_products(request.product_a, request.product_b)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
