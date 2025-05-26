from fastapi import APIRouter, Depends

from app import models, schemas
from app.db.session import get_db

router = APIRouter(tags=["User Profile Management"])

@router.get(
    "/me", 
    response_model=schemas.UserRead,
    summary="Get current user's profile",
    description="Retrieves the profile information for the currently authenticated user.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "User not authenticated."},
    }
)
async def read_users_me(
    current_user: models.User = Depends(get_current_active_user),
):
    return current_user

@router.put(
    "/me", 
    response_model=schemas.UserRead,
    summary="Update current user's profile",
    description="Allows the currently authenticated user to update their profile information. Only provided fields will be updated.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "User not authenticated."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error on input data."}
    }
)
async def update_user_me(
    user_in: schemas.UserProfileUpdate,
    db_session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    updated_user = await crud.crud_user.update_user_profile(
        db_session=db_session, user_obj=current_user, user_in=user_in
    )
    return updated_user
