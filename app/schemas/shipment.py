import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.schemas.address import AddressSchema

class ShipmentBase(BaseModel):
    pickup_address: AddressSchema
    delivery_address: AddressSchema
    pickup_datetime_window_start: Optional[datetime] = None
    pickup_datetime_window_end: Optional[datetime] = None
    delivery_datetime_window_start: Optional[datetime] = None
    delivery_datetime_window_end: Optional[datetime] = None
    status: str = "pending"
    service_level: str
    cost: Optional[float] = None
    package_details: Optional[str] = None
    special_instructions: Optional[str] = None

from app.schemas.enums import ShipmentStatusEnum

class ShipmentStatusUpdate(BaseModel):
    status: ShipmentStatusEnum

class ShipmentCreate(ShipmentBase):
    pass

class ShipmentRead(ShipmentBase):
    id: uuid.UUID
    tracking_number: str
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ShipmentUpdate(BaseModel):
    pickup_address: Optional[AddressSchema] = None
    delivery_address: Optional[AddressSchema] = None
    pickup_datetime_window_start: Optional[datetime] = None
    pickup_datetime_window_end: Optional[datetime] = None
    delivery_datetime_window_start: Optional[datetime] = None
    delivery_datetime_window_end: Optional[datetime] = None
    status: Optional[str] = None
    service_level: Optional[str] = None
    cost: Optional[float] = None
    package_details: Optional[str] = None
    special_instructions: Optional[str] = None
