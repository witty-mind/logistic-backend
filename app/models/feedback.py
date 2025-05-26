import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, func, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey("shipments.id"), nullable=True)
    
    rating = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=func.now())

    user = relationship("User")
    shipment = relationship("Shipment")

    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )
