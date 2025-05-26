import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas, crud
from app.core.security import get_current_active_user
from app.db.session import get_db

router = APIRouter(tags=["Feedback Management"])

@router.post(
    "/", 
    response_model=schemas.FeedbackRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Submit new feedback",
    description="Allows an authenticated user to submit feedback, optionally linking it to one of their shipments.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Shipment not found or not owned by user (if shipment_id provided)."},
        status.HTTP_401_UNAUTHORIZED: {"description": "User not authenticated."},
    }
)
async def create_feedback_endpoint(
    feedback_in: schemas.FeedbackCreate,
    db_session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    if feedback_in.shipment_id:
        shipment = await crud.crud_shipment.get_shipment_by_id(db_session=db_session, shipment_id=feedback_in.shipment_id)
        if not shipment or shipment.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipment not found or not owned by user.",
            )
            
    feedback = await crud.crud_feedback.create_feedback(
        db_session=db_session, feedback_in=feedback_in, user_id=current_user.id
    )
    return feedback

@router.get(
    "/shipment/{shipment_id}", 
    response_model=List[schemas.FeedbackRead],
    summary="Get feedback for a specific shipment",
    description="Retrieves all feedback associated with a specific shipment ID. Requires the authenticated user to own the shipment or be an admin (admin logic not implemented).",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Shipment not found."},
        status.HTTP_403_FORBIDDEN: {"description": "Not authorized to view feedback for this shipment."},
        status.HTTP_401_UNAUTHORIZED: {"description": "User not authenticated."},
    }
)
async def get_feedback_for_shipment_endpoint(
    shipment_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    shipment = await crud.crud_shipment.get_shipment_by_id(db_session=db_session, shipment_id=shipment_id)
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found.",
        )
    if shipment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view feedback for this shipment.",
        )
        
    feedback_list = await crud.crud_feedback.get_feedback_by_shipment(
        db_session=db_session, shipment_id=shipment_id
    )
    return feedback_list

@router.get(
    "/user/me", 
    response_model=List[schemas.FeedbackRead],
    summary="Get feedback submitted by the current user",
    description="Retrieves all feedback submitted by the currently authenticated user.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "User not authenticated."},
    }
)
async def get_my_feedback_endpoint(
    db_session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    feedback_list = await crud.crud_feedback.get_feedback_by_user(
        db_session=db_session, user_id=current_user.id
    )
    return feedback_list
