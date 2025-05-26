import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class SupportTicketBase(BaseModel):
    subject: str
    description: str

class SupportTicketCreate(SupportTicketBase):
    pass

class SupportTicketRead(SupportTicketBase):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class SupportTicketUpdate(BaseModel):
    status: str
