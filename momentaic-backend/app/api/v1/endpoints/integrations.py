"""
Integration Endpoints
Connect and manage external services
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import structlog

from app.core.database import get_db
from app.core.security import get_current_active_user, verify_startup_access
from app.models.user import User
from app.models.integration import (
    Integration, IntegrationData, IntegrationProvider, IntegrationStatus
)

logger = structlog.get_logger()
router = APIRouter()


# ==================
# Schemas
# ==================

class IntegrationCreate(BaseModel):
    """Create integration request"""
    provider: IntegrationProvider
    name: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    config: dict = {}


class IntegrationResponse(BaseModel):
    """Integration response"""
    id: UUID
    provider: IntegrationProvider
    name: str
    status: IntegrationStatus
    last_sync_at: Optional[str] = None
    config: dict = {}

    class Config:
        from_attributes = True


class IntegrationDataResponse(BaseModel):
    """Integration data response"""
    category: str
    data_type: str
    data: dict
    synced_at: str


class SyncRequest(BaseModel):
    """Request to sync data"""
    data_types: Optional[List[str]] = None


# ==================
# Endpoints
# ==================

@router.get("", response_model=List[IntegrationResponse])
async def list_integrations(
    startup_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all integrations for a startup"""
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Integration).where(
            Integration.startup_id == startup_id,
            Integration.user_id == current_user.id,
        )
    )
    integrations = result.scalars().all()
    
    return [
        IntegrationResponse(
            id=i.id,
            provider=i.provider,
            name=i.name,
            status=i.status,
            last_sync_at=i.last_sync_at.isoformat() if i.last_sync_at else None,
            config=i.config,
        )
        for i in integrations
    ]


@router.post("", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    startup_id: UUID,
    integration_data: IntegrationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Connect a new integration"""
    await verify_startup_access(startup_id, current_user, db)
    
    # Check if already connected
    existing = await db.execute(
        select(Integration).where(
            Integration.startup_id == startup_id,
            Integration.provider == integration_data.provider,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{integration_data.provider.value} is already connected"
        )
    
    integration = Integration(
        user_id=current_user.id,
        startup_id=startup_id,
        provider=integration_data.provider,
        name=integration_data.name,
        api_key=integration_data.api_key,
        api_secret=integration_data.api_secret,
        config=integration_data.config,
        status=IntegrationStatus.ACTIVE if integration_data.api_key else IntegrationStatus.PENDING,
    )
    
    db.add(integration)
    await db.flush()
    
    logger.info("Integration created", provider=integration_data.provider.value)
    
    return IntegrationResponse(
        id=integration.id,
        provider=integration.provider,
        name=integration.name,
        status=integration.status,
        config=integration.config,
    )


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    startup_id: UUID,
    integration_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get integration details"""
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id,
            Integration.startup_id == startup_id,
        )
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    return IntegrationResponse(
        id=integration.id,
        provider=integration.provider,
        name=integration.name,
        status=integration.status,
        last_sync_at=integration.last_sync_at.isoformat() if integration.last_sync_at else None,
        config=integration.config,
    )


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    startup_id: UUID,
    integration_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect an integration"""
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id,
            Integration.startup_id == startup_id,
        )
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    await db.delete(integration)
    logger.info("Integration deleted", provider=integration.provider.value)


@router.post("/{integration_id}/sync")
async def sync_integration(
    startup_id: UUID,
    integration_id: UUID,
    sync_request: SyncRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Sync data from an integration"""
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id,
            Integration.startup_id == startup_id,
        )
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    # Import and use appropriate integration class
    from app.integrations import get_integration_class
    from app.integrations.base import IntegrationCredentials
    from datetime import datetime
    
    IntegrationClass = get_integration_class(integration.provider)
    
    if not IntegrationClass:
        return {
            "success": False,
            "message": f"Sync not implemented for {integration.provider.value}"
        }
    
    # Create integration instance with credentials and config
    credentials = IntegrationCredentials(
        access_token=integration.access_token,
        api_key=integration.api_key,
        api_secret=integration.api_secret,
    )
    
    integration_client = IntegrationClass(credentials, config=integration.config)
    
    try:
        sync_result = await integration_client.sync_data(sync_request.data_types)
        
        # Store synced data
        if sync_result.success and sync_result.data:
            for data_type, value in sync_result.data.items():
                data_record = IntegrationData(
                    integration_id=integration.id,
                    startup_id=startup_id,
                    category="metrics",
                    data_type=data_type,
                    data=value if isinstance(value, dict) else {"value": value},
                    metric_value=value if isinstance(value, (int, float)) else None,
                    synced_at=datetime.utcnow(),
                )
                db.add(data_record)
        
        # Update integration last sync
        integration.last_sync_at = datetime.utcnow()
        integration.status = IntegrationStatus.ACTIVE if sync_result.success else IntegrationStatus.ERROR
        if not sync_result.success:
            integration.last_error = "; ".join(sync_result.errors)
        
        await db.flush()
        
        return {
            "success": sync_result.success,
            "records_synced": sync_result.records_synced,
            "data": sync_result.data,
            "errors": sync_result.errors,
        }
    except Exception as e:
        logger.error("Sync failed", error=str(e))
        return {"success": False, "message": str(e)}
    finally:
        await integration_client.close()


@router.get("/{integration_id}/data", response_model=List[IntegrationDataResponse])
async def get_integration_data(
    startup_id: UUID,
    integration_id: UUID,
    data_type: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get synced data from an integration"""
    await verify_startup_access(startup_id, current_user, db)
    
    query = select(IntegrationData).where(
        IntegrationData.integration_id == integration_id,
        IntegrationData.startup_id == startup_id,
    )
    
    if data_type:
        query = query.where(IntegrationData.data_type == data_type)
    
    query = query.order_by(IntegrationData.synced_at.desc()).limit(limit)
    
    result = await db.execute(query)
    data_records = result.scalars().all()
    
    return [
        IntegrationDataResponse(
            category=d.category.value,
            data_type=d.data_type,
            data=d.data,
            synced_at=d.synced_at.isoformat(),
        )
        for d in data_records
    ]
