import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# Enum for status could be defined here or in enums.py
# from app.schemas.enums import SupportTicketStatusEnum 

class SupportTicketBase(BaseModel):
    subject: str = Field(..., description="Subject of the support ticket.", example="Issue with recent shipment")
    description: str = Field(..., description="Detailed description of the support issue.", example="My package ABC123XYZ has not arrived.")

    class Config:
        schema_extra = {
            "description": "Base schema for support ticket details."
        }

class SupportTicketCreate(SupportTicketBase):
    class Config:
        schema_extra = {
            "description": "Schema for creating a new support ticket."
        }

class SupportTicketRead(SupportTicketBase):
    id: uuid.UUID = Field(..., description="Unique ID of the support ticket.", example=uuid.uuid4())
    user_id: uuid.UUID = Field(..., description="ID of the user who created the support ticket.", example=uuid.uuid4())
    status: str = Field(..., description="Current status of the support ticket (e.g., open, in_progress, closed).", example="open")
    created_at: datetime = Field(..., description="Timestamp of when the support ticket was created.", example=datetime.utcnow())
    updated_at: datetime = Field(..., description="Timestamp of the last update to the support ticket.", example=datetime.utcnow())

    class Config:
        orm_mode = True
        schema_extra = {
            "description": "Schema for reading support ticket details, including all base fields and system-generated information."
        }

class SupportTicketUpdate(BaseModel):
    status: str = Field(..., description="New status for the support ticket (e.g., open, in_progress, closed).", example="closed") # Consider using an Enum here

    class Config:
        schema_extra = {
            "description": "Schema for updating the status of a support ticket."
        }
