from fastapi import APIRouter, Depends, HTTPException, status, Request # Add Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app import schemas
from app.core import security
from app.db.session import get_db
from app.main import limiter # Import the limiter instance

router = APIRouter(tags=["Authentication"])

@router.post(
    "/register", 
    response_model=schemas.UserRead,
    summary="Register a new user",
    description="Create a new user account. An email and password are required.",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Email already registered"},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Too many registration attempts"},
    }
)
@limiter.limit("10/minute") # Stricter limit for registration
async def register_user(
    request: Request, # Add request for limiter
    user_in: schemas.UserCreate, 
    db_session: AsyncSession = Depends(get_db)
):
    existing_user = await crud.crud_user.get_user_by_email(db_session=db_session, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = await crud.crud_user.create_user(db_session=db_session, user_in=user_in)
    return user

@router.post(
    "/login", 
    response_model=schemas.Token,
    summary="User login",
    description="Authenticate an existing user and receive JWT access and refresh tokens. Uses OAuth2PasswordRequestForm (form data: username & password).",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Incorrect email or password"},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Too many login attempts"},
    }
)
@limiter.limit("5/minute") # Stricter limit for login
async def login_for_access_token(
    request: Request, # Add request for limiter
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

@router.post(
    "/password-recovery/{email}", 
    status_code=status.HTTP_200_OK,
    summary="Request password recovery",
    description="Request a password recovery token for the specified email. If the user exists, a token is generated (and in a real app, emailed).",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "User with this email does not exist."},
        status.HTTP_200_OK: {"description": "Password recovery email sent (token logged to console for testing).", "content": {"application/json": {"example": {"msg": "Password recovery email sent (token logged to console)."}}}},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Too many password recovery attempts"},
    }
)
@limiter.limit("5/minute") # Stricter limit for password recovery
async def request_password_recovery(
    request: Request, # Add request for limiter
    email: str, 
    db_session: AsyncSession = Depends(get_db)
):
    user = await crud.crud_user.get_user_by_email(db_session=db_session, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist.",
        )

    password_reset_token = security.create_password_reset_token(email=email)
    print(f"Password reset token for {email}: {password_reset_token}") # For testing
    return {"msg": "Password recovery email sent (token logged to console)."}

@router.post(
    "/reset-password/", 
    status_code=status.HTTP_200_OK,
    summary="Reset password",
    description="Reset the user's password using a valid password reset token and a new password.",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid or expired password reset token."},
        status.HTTP_404_NOT_FOUND: {"description": "User not found (should not typically occur if token is valid)."},
        status.HTTP_200_OK: {"description": "Password has been reset successfully.", "content": {"application/json": {"example": {"msg": "Password has been reset successfully."}}}},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Too many password reset attempts"},
    }
)
@limiter.limit("5/minute") # Stricter limit for password reset
async def reset_password(
    request: Request, # Add request for limiter
    reset_data: schemas.PasswordReset, 
    db_session: AsyncSession = Depends(get_db)
):
    email = security.verify_password_reset_token(token=reset_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )
    
    user = await crud.crud_user.get_user_by_email(db_session=db_session, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    hashed_password = security.get_password_hash(reset_data.new_password)
    user.hashed_password = hashed_password
    db_session.add(user)
    await db_session.commit()
    
    return {"msg": "Password has been reset successfully."}
