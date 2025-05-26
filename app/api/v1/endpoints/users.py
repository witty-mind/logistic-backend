from fastapi import APIRouter, Depends

from app import models, schemas
from app.core.security import get_current_active_user

router = APIRouter()

@router.get("/me", response_model=schemas.UserRead)
async def read_users_me(
    current_user: models.User = Depends(get_current_active_user),
):
    return current_user

@router.put("/me", response_model=schemas.UserRead)
async def update_user_me(
    user_in: schemas.UserProfileUpdate,
    db_session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    updated_user = await crud.crud_user.update_user_profile(
        db_session=db_session, user_obj=current_user, user_in=user_in
    )
    return updated_user
