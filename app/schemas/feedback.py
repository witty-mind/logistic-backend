import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, conint, Field

class FeedbackBase(BaseModel):
    rating: conint(ge=1, le=5) = Field(..., description="User rating on a scale of 1 to 5.", example=5)
    comment: Optional[str] = Field(None, description="User comment for the feedback.", example="Excellent service!")
    shipment_id: Optional[uuid.UUID] = Field(None, description="Optional ID of the shipment this feedback is related to.", example=uuid.uuid4())
    
    class Config:
        schema_extra = {
            "description": "Base schema for feedback, including rating and an optional comment and shipment ID."
        }

class FeedbackCreate(FeedbackBase):
    class Config:
        schema_extra = {
            "description": "Schema for creating new feedback."
        }

class FeedbackRead(FeedbackBase):
    id: uuid.UUID = Field(..., description="Unique ID of the feedback.", example=uuid.uuid4())
    user_id: uuid.UUID = Field(..., description="ID of the user who submitted the feedback.", example=uuid.uuid4())
    created_at: datetime = Field(..., description="Timestamp of when the feedback was created.", example=datetime.utcnow())

    class Config:
        orm_mode = True
        schema_extra = {
            "description": "Schema for reading feedback, including all base fields plus system-generated IDs and timestamps."
        }
