from pydantic import BaseModel, EmailStr

class AddressSchema(BaseModel):
    address_line1: str
    city: str
    postal_code: str
    contact_name: str
    contact_phone: str
    contact_email: EmailStr
