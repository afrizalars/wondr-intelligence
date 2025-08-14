from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.database import Base
import uuid

class Guardrail(Base):
    __tablename__ = "guardrails"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    rule_type = Column(String, nullable=False)  # regex, keyword, semantic
    pattern = Column(Text, nullable=False)
    action = Column(String, nullable=False)  # block, warn, flag, transform
    severity = Column(String, default='low')  # low, medium, high, critical
    message = Column(Text)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=100)
    meta_data = Column("metadata", JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())