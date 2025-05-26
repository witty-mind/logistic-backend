import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, conint

class FeedbackBase(BaseModel):
    rating: conint(ge=1, le=5) # Constrained integer for rating 1-5
    comment: Optional[str] = None
    shipment_id: Optional[uuid.UUID] = None

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackRead(FeedbackBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True
