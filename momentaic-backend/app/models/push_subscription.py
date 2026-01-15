from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Boolean, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

from sqlalchemy.dialects.postgresql import UUID

class PushSubscription(Base):
    __tablename__ = "push_subscriptions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Standard Web Push fields
    endpoint = Column(String, nullable=False)
    p256dh = Column(String, nullable=False) 
    auth = Column(String, nullable=False)
    
    # Metadata
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", backref="push_subscriptions")

    __table_args__ = (
        Index('ix_push_subs_user_endpoint', 'user_id', 'endpoint', unique=True),
    )
