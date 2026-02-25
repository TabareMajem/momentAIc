import uuid
import enum
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, UTC
from app.core.database import Base

class TelecomProvider(str, enum.Enum):
    TWILIO = "twilio"
    VAPI = "vapi"
    RETELL = "retell"

class ProvisionedNumber(Base):
    __tablename__ = "telecom_numbers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    startup_id = Column(UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False)
    provider = Column(Enum(TelecomProvider, native_enum=False), default=TelecomProvider.TWILIO, nullable=False)
    phone_number = Column(String, nullable=False, unique=True, index=True)
    friendly_name = Column(String, nullable=True)
    
    # Twilio specific metadata
    sid = Column(String, nullable=True)
    language = Column(String(20), default="en-US", nullable=False)
    
    # Internal agent mapping
    agent_id = Column(String, nullable=True) # ID of the character/agent handling this line
    active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
