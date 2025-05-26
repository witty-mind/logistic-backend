import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.support_ticket import SupportTicket
from app.schemas.support_ticket import SupportTicketCreate


async def create_support_ticket(
    db_session: AsyncSession, *, ticket_in: SupportTicketCreate, user_id: uuid.UUID
) -> SupportTicket:
    db_ticket = SupportTicket(
        **ticket_in.model_dump(),
        user_id=user_id
    )
    db_session.add(db_ticket)
    await db_session.commit()
    await db_session.refresh(db_ticket)
    return db_ticket

async def get_support_ticket_by_id(
    db_session: AsyncSession, *, ticket_id: uuid.UUID
) -> Optional[SupportTicket]:
    result = await db_session.execute(
        select(SupportTicket).filter(SupportTicket.id == ticket_id)
    )
    return result.scalars().first()

async def get_support_tickets_by_user(
    db_session: AsyncSession, *, user_id: uuid.UUID
) -> List[SupportTicket]:
    result = await db_session.execute(
        select(SupportTicket).filter(SupportTicket.user_id == user_id).order_by(SupportTicket.created_at.desc())
    )
    return result.scalars().all()

async def update_support_ticket_status(
    db_session: AsyncSession, *, ticket_id: uuid.UUID, status: str
) -> Optional[SupportTicket]:
    db_ticket = await get_support_ticket_by_id(db_session=db_session, ticket_id=ticket_id)
    if not db_ticket:
        return None
    
    db_ticket.status = status
    db_session.add(db_ticket) # updated_at is handled by the model's onupdate
    await db_session.commit()
    await db_session.refresh(db_ticket)
    return db_ticket
