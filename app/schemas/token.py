from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class Token(BaseModel):
    access_token: str = Field(..., description="The JWT access token.", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    refresh_token: str = Field(..., description="The JWT refresh token.", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field("bearer", description="The type of token (always 'bearer').", example="bearer")

    class Config:
        schema_extra = {
            "description": "Schema for returning JWT access and refresh tokens."
        }

class TokenData(BaseModel):
    email: Optional[EmailStr] = Field(None, description="Email address extracted from the token's subject.", example="user@example.com")

    class Config:
        schema_extra = {
            "description": "Schema representing the data encoded within a JWT, typically the user's email."
        }
