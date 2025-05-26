import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate


async def create_feedback(
    db_session: AsyncSession, *, feedback_in: FeedbackCreate, user_id: uuid.UUID
) -> Feedback:
    db_feedback = Feedback(
        **feedback_in.model_dump(), 
        user_id=user_id
    )
    db_session.add(db_feedback)
    await db_session.commit()
    await db_session.refresh(db_feedback)
    return db_feedback

async def get_feedback_by_shipment(
    db_session: AsyncSession, *, shipment_id: uuid.UUID
) -> List[Feedback]:
    result = await db_session.execute(
        select(Feedback).filter(Feedback.shipment_id == shipment_id).order_by(Feedback.created_at.desc())
    )
    return result.scalars().all()

async def get_feedback_by_user(
    db_session: AsyncSession, *, user_id: uuid.UUID
) -> List[Feedback]:
    result = await db_session.execute(
        select(Feedback).filter(Feedback.user_id == user_id).order_by(Feedback.created_at.desc())
    )
    return result.scalars().all()
