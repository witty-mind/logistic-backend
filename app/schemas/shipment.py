import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.schemas.address import AddressSchema
from app.schemas.enums import PricingTierEnum, ShipmentStatusEnum # Combined imports
from pydantic import Field # Import Field

# Example address for documentation
example_address = {
    "address_line1": "123 Main St", "city": "Anytown", "postal_code": "12345",
    "contact_name": "John Doe", "contact_phone": "555-0100", "contact_email": "john.doe@example.com"
}

class ShipmentBase(BaseModel):
    pickup_address: AddressSchema = Field(..., description="Details of the pickup address.")
    delivery_address: AddressSchema = Field(..., description="Details of the delivery address.")
    pickup_datetime_window_start: Optional[datetime] = Field(None, description="Start of the pickup time window.", example=datetime.utcnow())
    pickup_datetime_window_end: Optional[datetime] = Field(None, description="End of the pickup time window.", example=datetime.utcnow())
    delivery_datetime_window_start: Optional[datetime] = Field(None, description="Start of the delivery time window.", example=datetime.utcnow())
    delivery_datetime_window_end: Optional[datetime] = Field(None, description="End of the delivery time window.", example=datetime.utcnow())
    status: str = Field("pending", description="Current status of the shipment.", example="pending")
    service_level: PricingTierEnum = Field(..., description="Selected service level for the shipment.", example=PricingTierEnum.STANDARD)
    cost: Optional[float] = Field(None, description="Calculated cost of the shipment.", example=10.0)
    package_details: Optional[str] = Field(None, description="Details about the package being shipped.", example="1 box, 5kg, fragile")
    special_instructions: Optional[str] = Field(None, description="Any special instructions for the shipment.", example="Handle with care.")

    class Config:
        schema_extra = {
            "description": "Base schema for shipment details.",
            "example": {
                "pickup_address": example_address,
                "delivery_address": {**example_address, "address_line1": "456 Other St"},
                "pickup_datetime_window_start": "2023-01-01T09:00:00Z",
                "pickup_datetime_window_end": "2023-01-01T12:00:00Z",
                "status": "pending",
                "service_level": PricingTierEnum.STANDARD,
                "package_details": "1 box, 5kg",
            }
        }

class ShipmentStatusUpdate(BaseModel):
    status: ShipmentStatusEnum = Field(..., description="The new status for the shipment.", example=ShipmentStatusEnum.IN_TRANSIT)
    
    class Config:
        schema_extra = {
            "description": "Schema for updating the status of a shipment."
        }

class ShipmentCreate(ShipmentBase):
    class Config:
        schema_extra = {
            "description": "Schema for creating a new shipment. Cost is calculated automatically."
        }


class ShipmentRead(ShipmentBase):
    id: uuid.UUID = Field(..., description="Unique ID of the shipment.", example=uuid.uuid4())
    tracking_number: str = Field(..., description="Unique tracking number for the shipment.", example="ABC123XYZ789")
    user_id: uuid.UUID = Field(..., description="ID of the user who created the shipment.", example=uuid.uuid4())
    created_at: datetime = Field(..., description="Timestamp of when the shipment was created.", example=datetime.utcnow())
    updated_at: datetime = Field(..., description="Timestamp of the last update to the shipment.", example=datetime.utcnow())

    class Config:
        orm_mode = True
        schema_extra = {
            "description": "Schema for reading shipment details, including all base fields and system-generated information."
        }

class ShipmentUpdate(BaseModel):
    pickup_address: Optional[AddressSchema] = Field(None, description="Updated pickup address details.")
    delivery_address: Optional[AddressSchema] = Field(None, description="Updated delivery address details.")
    pickup_datetime_window_start: Optional[datetime] = Field(None, description="Updated start of the pickup time window.")
    pickup_datetime_window_end: Optional[datetime] = Field(None, description="Updated end of the pickup time window.")
    delivery_datetime_window_start: Optional[datetime] = Field(None, description="Updated start of the delivery time window.")
    delivery_datetime_window_end: Optional[datetime] = Field(None, description="Updated end of the delivery time window.")
    status: Optional[ShipmentStatusEnum] = Field(None, description="Updated status of the shipment. Note: For direct status updates, prefer the dedicated /status endpoint.") # Added enum
    service_level: Optional[PricingTierEnum] = Field(None, description="Updated service level for the shipment.") # Added enum
    cost: Optional[float] = Field(None, description="Updated cost of the shipment (typically system-calculated).")
    package_details: Optional[str] = Field(None, description="Updated package details.")
    special_instructions: Optional[str] = Field(None, description="Updated special instructions.")

    class Config:
        schema_extra = {
            "description": "Schema for updating shipment details. Only provided fields will be updated."
        }
