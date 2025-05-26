import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    
    # Extended fields for UserRead
    name: Optional[str] = None
    phone: Optional[str] = None
    default_address_json: Optional[dict] = None # Or AddressSchema if preferred
    email_notifications_enabled: Optional[bool] = None
    sms_notifications_enabled: Optional[bool] = None
    terms_accepted_at: Optional[datetime] = None
    default_service_level: Optional[str] = None
    preferred_pickup_window_start: Optional[str] = None
    preferred_pickup_window_end: Optional[str] = None


    class Config:
        orm_mode = True

# UserProfileUpdate Schema
class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    default_address_json: Optional[dict] = None # Or AddressSchema
    email_notifications_enabled: Optional[bool] = None
    sms_notifications_enabled: Optional[bool] = None
    terms_accepted_at: Optional[datetime] = None # Or a way to mark as accepted now
    default_service_level: Optional[str] = None
    preferred_pickup_window_start: Optional[str] = None
    preferred_pickup_window_end: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str
