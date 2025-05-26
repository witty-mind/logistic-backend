import uuid
from sqlalchemy import Column, String, Boolean, DateTime, func, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid # Ensure uuid is imported

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # New profile fields
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    # Storing default_address as JSON for now as per instructions
    default_address_json = Column(JSON, nullable=True) 
    email_notifications_enabled = Column(Boolean, default=True)
    sms_notifications_enabled = Column(Boolean, default=False)
    terms_accepted_at = Column(DateTime, nullable=True)
    default_service_level = Column(String, nullable=True) 
    preferred_pickup_window_start = Column(String, nullable=True) # e.g., "09:00"
    preferred_pickup_window_end = Column(String, nullable=True)   # e.g., "17:00"
