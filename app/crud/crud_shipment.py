import uuid
from typing import List, Optional # This was already here, my mistake. No change needed here.

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.shipment import Shipment
from app.schemas.shipment import ShipmentCreate, ShipmentUpdate
# Ensure Optional is imported if not already (it was, but checking)
from typing import Optional


async def create_shipment(
    db_session: AsyncSession, *, shipment_in: ShipmentCreate, user_id: uuid.UUID, tracking_number: str
) -> Shipment:
    db_shipment = Shipment(
        **shipment_in.model_dump(), 
        user_id=user_id, 
        tracking_number=tracking_number
    )
    db_session.add(db_shipment)
    await db_session.commit()
    await db_session.refresh(db_shipment)
    return db_shipment

async def get_shipment_by_tracking_number(
    db_session: AsyncSession, *, tracking_number: str
) -> Optional[Shipment]:
    result = await db_session.execute(
        select(Shipment).filter(Shipment.tracking_number == tracking_number)
    )
    return result.scalars().first()

async def get_shipments_by_user_id(
    db_session: AsyncSession, *, user_id: uuid.UUID, status: Optional[str] = None, skip: int = 0, limit: int = 100
) -> List[Shipment]:
    query = select(Shipment).filter(Shipment.user_id == user_id)
    
    if status:
        query = query.filter(Shipment.status.ilike(f"%{status}%")) # Case-insensitive filter
        
    query = query.offset(skip).limit(limit).order_by(Shipment.created_at.desc())
    
    result = await db_session.execute(query)
    return result.scalars().all()

async def get_shipment_by_id(
    db_session: AsyncSession, *, shipment_id: uuid.UUID
) -> Optional[Shipment]:
    result = await db_session.execute(
        select(Shipment).filter(Shipment.id == shipment_id)
    )
    return result.scalars().first()

async def update_shipment_status(
    db_session: AsyncSession, *, shipment_id: uuid.UUID, new_status: str
) -> Optional[Shipment]:
    db_shipment = await get_shipment_by_id(db_session=db_session, shipment_id=shipment_id)
    if not db_shipment:
        return None
    
    db_shipment.status = new_status
    # updated_at is handled by the model's onupdate=func.now() or database default
    db_session.add(db_shipment)
    await db_session.commit()
    await db_session.refresh(db_shipment)
    return db_shipment

async def update_shipment(
    db_session: AsyncSession, *, db_shipment: Shipment, shipment_in: ShipmentUpdate
) -> Shipment:
    update_data = shipment_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_shipment, key, value)
    
    db_session.add(db_shipment)
    await db_session.commit()
    await db_session.refresh(db_shipment)
    return db_shipment

async def delete_shipment(db_session: AsyncSession, *, db_shipment: Shipment) -> None:
    await db_session.delete(db_shipment)
    await db_session.commit()
