import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Float, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base

class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tracking_number = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    pickup_address = Column(JSON, nullable=False)
    delivery_address = Column(JSON, nullable=False)
    
    pickup_datetime_window_start = Column(DateTime, nullable=True)
    pickup_datetime_window_end = Column(DateTime, nullable=True)
    delivery_datetime_window_start = Column(DateTime, nullable=True)
    delivery_datetime_window_end = Column(DateTime, nullable=True)
    
    status = Column(String, index=True, nullable=False, default="pending")
    service_level = Column(String, index=True, nullable=False)
    cost = Column(Float, nullable=True)
    
    package_details = Column(String, nullable=True)
    special_instructions = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User")
