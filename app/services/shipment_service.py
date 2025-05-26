import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_shipment
from app.models.shipment import Shipment
from app.schemas.shipment import ShipmentCreate
from app.services.pricing_service import pricing_service # Import the pricing_service instance


async def create_new_shipment(
    db_session: AsyncSession, *, shipment_in: ShipmentCreate, user_id: uuid.UUID
) -> Shipment:
    # Generate a unique tracking number
    tracking_number = uuid.uuid4().hex[:10].upper()
    
    # Calculate shipment cost using the pricing service
    # Assuming shipment_in.service_level is a string representation of the enum, e.g., "EXPRESS"
    # If shipment_in.service_level is an enum member, use shipment_in.service_level.value
    # Based on current setup, ShipmentCreate will have service_level as PricingTierEnum, so .value is needed.
    calculated_cost = pricing_service.calculate_shipment_cost(
        service_level=shipment_in.service_level.value # Use .value for enum
    )

    created_shipment = await crud_shipment.create_shipment(
        db_session=db_session,
        shipment_in=shipment_in,
        user_id=user_id,
        tracking_number=tracking_number,
        cost=calculated_cost  # Pass the calculated cost
    )
    return created_shipment
