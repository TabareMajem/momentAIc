from sqlalchemy import Column, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum
import uuid

class ViralAssetStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    POSTED = "posted"
    REJECTED = "rejected"

class ViralAsset(Base):
    __tablename__ = "viral_assets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_topic = Column(String, nullable=False, index=True)
    hook_text = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    status = Column(Enum(ViralAssetStatus, native_enum=False), default=ViralAssetStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
