import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_shipment
from app.models.shipment import Shipment
from app.schemas.shipment import ShipmentCreate


async def create_new_shipment(
    db_session: AsyncSession, *, shipment_in: ShipmentCreate, user_id: uuid.UUID
) -> Shipment:
    # Generate a unique tracking number
    # For simplicity, using a portion of UUID. In a real-world scenario, 
    # you might want a more robust system to ensure uniqueness under high load,
    # potentially checking the DB in a loop or using a dedicated sequence/service.
    tracking_number = uuid.uuid4().hex[:10].upper() 
    
    # Potentially add a loop here to ensure tracking_number is unique if high collision risk
    # while await crud_shipment.get_shipment_by_tracking_number(db_session, tracking_number=tracking_number):
    #     tracking_number = uuid.uuid4().hex[:10].upper()

    created_shipment = await crud_shipment.create_shipment(
        db_session=db_session, 
        shipment_in=shipment_in, 
        user_id=user_id, 
        tracking_number=tracking_number
    )
    return created_shipment
