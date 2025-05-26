from pydantic import BaseModel, EmailStr, Field

class AddressSchema(BaseModel):
    address_line1: str = Field(..., example="123 Main Street")
    city: str = Field(..., example="Anytown")
    postal_code: str = Field(..., example="12345")
    contact_name: str = Field(..., example="Jane Doe")
    contact_phone: str = Field(..., example="555-123-4567")
    contact_email: EmailStr = Field(..., example="jane.doe@example.com")

    class Config:
        schema_extra = {
            "description": "Represents a physical address with contact details."
        }
