from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate


async def create_user(db_session: AsyncSession, *, user_in: UserCreate) -> User:
    hashed_password = get_password_hash(user_in.password)
    db_user = User(email=user_in.email, hashed_password=hashed_password)
    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)
    return db_user


async def get_user_by_email(db_session: AsyncSession, *, email: str) -> User | None:
    result = await db_session.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def update_user_profile(
    db_session: AsyncSession, *, user_obj: User, user_in: schemas.UserProfileUpdate
) -> User:
    update_data = user_in.model_dump(exclude_unset=True)
    
    # Special handling for terms_accepted_at - if present in input, set to now if not already set
    if "terms_accepted_at" in update_data and update_data["terms_accepted_at"] is not None:
        if user_obj.terms_accepted_at is None: # Only set if not previously accepted or explicitly re-accepted
            user_obj.terms_accepted_at = datetime.utcnow()
        del update_data["terms_accepted_at"] # Remove from general update to avoid overriding with None

    for field, value in update_data.items():
        setattr(user_obj, field, value)
        
    db_session.add(user_obj)
    await db_session.commit()
    await db_session.refresh(user_obj)
    return user_obj
