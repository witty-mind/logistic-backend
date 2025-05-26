import uuid
from datetime import datetime
from typing import Optional, Dict # Import Dict
from pydantic import BaseModel, EmailStr, Field # Import Field

example_user_address = {
    "address_line1": "123 User Lane", "city": "UserCity", "postal_code": "54321",
    "contact_name": "Current User", "contact_phone": "555-000-1111", "contact_email": "current.user@example.com"
}

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user.", example="user@example.com")
    
    class Config:
        schema_extra = {
            "description": "Base schema for user details, primarily containing the email."
        }

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password for the new user account. Minimum 8 characters.", example="a_strong_password")
    
    class Config:
        schema_extra = {
            "description": "Schema for creating a new user, requiring email and password."
        }

class UserRead(UserBase):
    id: uuid.UUID = Field(..., description="Unique ID of the user.", example=uuid.uuid4())
    is_active: bool = Field(True, description="Indicates if the user account is active.", example=True)
    created_at: datetime = Field(..., description="Timestamp of when the user account was created.", example=datetime.utcnow())
    
    # Extended fields for UserRead
    name: Optional[str] = Field(None, description="Full name of the user.", example="Johnathan Doe")
    phone: Optional[str] = Field(None, description="Contact phone number for the user.", example="555-987-6543")
    default_address_json: Optional[Dict] = Field(None, description="Default address for the user, stored as JSON.", example=example_user_address) # Or AddressSchema
    email_notifications_enabled: Optional[bool] = Field(True, description="Indicates if email notifications are enabled for the user.", example=True)
    sms_notifications_enabled: Optional[bool] = Field(False, description="Indicates if SMS notifications are enabled for the user.", example=False)
    terms_accepted_at: Optional[datetime] = Field(None, description="Timestamp of when the user accepted terms and conditions.", example=datetime.utcnow())
    default_service_level: Optional[str] = Field(None, description="User's preferred default service level.", example="STANDARD")
    preferred_pickup_window_start: Optional[str] = Field(None, description="User's preferred pickup window start time (HH:MM).", example="09:00")
    preferred_pickup_window_end: Optional[str] = Field(None, description="User's preferred pickup window end time (HH:MM).", example="17:00")

    class Config:
        orm_mode = True
        schema_extra = {
            "description": "Schema for reading user details, including profile information and system-generated fields."
        }

# UserProfileUpdate Schema
class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Full name of the user.", example="John Doe")
    phone: Optional[str] = Field(None, description="Contact phone number for the user.", example="555-123-4567")
    default_address_json: Optional[Dict] = Field(None, description="Default address for the user, stored as JSON.", example=example_user_address) # Or AddressSchema
    email_notifications_enabled: Optional[bool] = Field(None, description="Enable or disable email notifications.", example=True)
    sms_notifications_enabled: Optional[bool] = Field(None, description="Enable or disable SMS notifications.", example=False)
    terms_accepted_at: Optional[datetime] = Field(None, description="Timestamp for accepting terms. Set to current time if user accepts.", example=datetime.utcnow())
    default_service_level: Optional[str] = Field(None, description="User's preferred default service level.", example="EXPRESS")
    preferred_pickup_window_start: Optional[str] = Field(None, description="User's preferred pickup window start time (HH:MM).", example="10:00")
    preferred_pickup_window_end: Optional[str] = Field(None, description="User's preferred pickup window end time (HH:MM).", example="18:00")

    class Config:
        schema_extra = {
            "description": "Schema for updating user profile information. Only provided fields will be updated."
        }

class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user requesting a password reset.", example="user@example.com")

    class Config:
        schema_extra = {
            "description": "Schema for requesting a password reset. Requires the user's email."
        }

class PasswordReset(BaseModel):
    token: str = Field(..., description="The password reset token received by the user.", example="eyJhbGciOiJIUzI1NiIs...")
    new_password: str = Field(..., min_length=8, description="The new password for the user account. Minimum 8 characters.", example="a_new_strong_password")

    class Config:
        schema_extra = {
            "description": "Schema for resetting a user's password using a token."
        }
