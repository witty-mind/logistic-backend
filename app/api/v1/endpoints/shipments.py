from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.services import shipment_service
from app.crud import crud_shipment

router = APIRouter(tags=["Shipment Management"])

@router.post(
    "/", 
    response_model=schemas.ShipmentRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new shipment",
    description="Allows an authenticated user to create a new shipment. The cost is calculated automatically based on the selected service level.",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "An error occurred while creating the shipment."},
        status.HTTP_401_UNAUTHORIZED: {"description": "User not authenticated."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error (e.g., invalid service level)."}
    }
)
async def create_shipment_endpoint(
    shipment_in: schemas.ShipmentCreate,
    db_session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    try:
        shipment = await shipment_service.create_new_shipment(
            db_session=db_session, shipment_in=shipment_in, user_id=current_user.id
        )
        return shipment
    except ValueError as ve: # Catch specific errors like invalid service level
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve),
        )
    except Exception:
        # Log the exception e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the shipment.",
        )

@router.get(
    "/", 
    response_model=List[schemas.ShipmentRead],
    summary="List shipments for the current user",
    description="Retrieves a list of shipments created by the currently authenticated user. Supports pagination and filtering by status.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "User not authenticated."},
    }
)
async def get_user_shipments_endpoint(
    db_session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
    status: Optional[schemas.ShipmentStatusEnum] = None,
    skip: int = 0,
    limit: int = 100,
):
    shipments = await crud_shipment.get_shipments_by_user_id(
        db_session=db_session, 
        user_id=current_user.id, 
        status=status.value if status else None,
        skip=skip, 
        limit=limit
    )
    return shipments

@router.get(
    "/{tracking_number}", 
    response_model=schemas.ShipmentRead,
    summary="Get a specific shipment by tracking number",
    description="Retrieves details for a specific shipment using its tracking number. Requires the authenticated user to own the shipment.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Shipment not found or user not authorized."},
        status.HTTP_401_UNAUTHORIZED: {"description": "User not authenticated."},
    }
)
async def get_shipment_by_tracking_number_endpoint(
    tracking_number: str,
    db_session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    shipment = await crud_shipment.get_shipment_by_tracking_number(
        db_session=db_session, tracking_number=tracking_number
    )
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found.",
        )
    if shipment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Shipment not found or not authorized.",
        )
    return shipment

@router.patch(
    "/{shipment_id}/status", 
    response_model=schemas.ShipmentRead,
    summary="Update a shipment's status",
    description="Allows an authenticated user to update the status of a shipment they own. (Further business logic for status transitions might apply).",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Shipment not found."},
        status.HTTP_403_FORBIDDEN: {"description": "Not authorized to update this shipment's status."},
        status.HTTP_401_UNAUTHORIZED: {"description": "User not authenticated."},
    }
)
async def update_shipment_status_endpoint(
    shipment_id: uuid.UUID,
    status_update: schemas.ShipmentStatusUpdate,
    db_session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    shipment = await crud_shipment.get_shipment_by_id(
        db_session=db_session, shipment_id=shipment_id
    )

    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found.",
        )

    if shipment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this shipment's status.",
        )

    updated_shipment = await crud_shipment.update_shipment_status(
        db_session=db_session, 
        shipment_id=shipment_id, 
        new_status=status_update.status.value
    )
    
    if not updated_shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, # Should be rare if first check passes
            detail="Shipment not found during update.",
        )
        
    return updated_shipment
