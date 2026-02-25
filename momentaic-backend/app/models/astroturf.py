import uuid
import enum
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, UTC
from app.core.database import Base

class MentionStatus(str, enum.Enum):
    PENDING = "pending"
    DRAFTED = "drafted"
    DEPLOYED = "deployed"
    DISMISSED = "dismissed"

class AstroTurfMention(Base):
    __tablename__ = "astroturf_mentions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    startup_id = Column(UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String, nullable=False)  # reddit, hackernews, twitter
    author = Column(String, nullable=False)
    content = Column(String, nullable=False)
    url = Column(String, nullable=False)
    generated_reply = Column(String, nullable=True)
    status = Column(Enum(MentionStatus), default=MentionStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
