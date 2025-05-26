from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app import schemas
from app.core import security
from app.db.session import get_db

router = APIRouter()

@router.post("/register", response_model=schemas.UserRead)
async def register_user(
    user_in: schemas.UserCreate, db_session: AsyncSession = Depends(get_db)
):
    existing_user = await crud.crud_user.get_user_by_email(db_session=db_session, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = await crud.crud_user.create_user(db_session=db_session, user_in=user_in)
    return user

@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    db_session: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await crud.crud_user.get_user_by_email(db_session=db_session, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(subject=user.email)
    refresh_token = security.create_refresh_token(subject=user.email)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/password-recovery/{email}", status_code=status.HTTP_200_OK)
async def request_password_recovery(
    email: str, db_session: AsyncSession = Depends(get_db)
):
    user = await crud.crud_user.get_user_by_email(db_session=db_session, email=email)
    if not user:
        # To prevent user enumeration, we can return a success message even if the user doesn't exist.
        # Or, raise a specific error if preferred. For this example, we'll just return a generic success.
        # In a real app, you might log this attempt or handle it differently.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist.",
        )

    password_reset_token = security.create_password_reset_token(email=email)
    # In a real application, you would send an email with this token.
    # For now, we can print it or return it (for testing).
    print(f"Password reset token for {email}: {password_reset_token}") # Logging for now
    return {"msg": "Password recovery email sent (token logged to console)."}

@router.post("/reset-password/", status_code=status.HTTP_200_OK)
async def reset_password(
    reset_data: schemas.PasswordReset, db_session: AsyncSession = Depends(get_db)
):
    email = security.verify_password_reset_token(token=reset_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )
    
    user = await crud.crud_user.get_user_by_email(db_session=db_session, email=email)
    if not user:
        # This case should ideally not happen if token generation is tied to existing users
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    hashed_password = security.get_password_hash(reset_data.new_password)
    user.hashed_password = hashed_password
    db_session.add(user)
    await db_session.commit()
    
    return {"msg": "Password has been reset successfully."}
