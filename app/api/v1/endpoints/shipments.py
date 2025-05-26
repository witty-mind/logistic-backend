from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.services import shipment_service
from app.crud import crud_shipment

router = APIRouter()

@router.post("/", response_model=schemas.ShipmentRead, status_code=status.HTTP_201_CREATED)
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
    except Exception as e:
        # Log the exception e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the shipment.",
        )

@router.get("/", response_model=List[schemas.ShipmentRead])
async def get_user_shipments_endpoint(
    db_session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
    status: Optional[schemas.ShipmentStatusEnum] = None, # Use the Enum for validation
    skip: int = 0,
    limit: int = 100,
):
    shipments = await crud_shipment.get_shipments_by_user_id(
        db_session=db_session, 
        user_id=current_user.id, 
        status=status.value if status else None, # Pass the enum's value
        skip=skip, 
        limit=limit
    )
    return shipments

@router.get("/{tracking_number}", response_model=schemas.ShipmentRead)
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
    # Ensure the user owns this shipment or is an admin (admin check not implemented here)
    if shipment.user_id != current_user.id:
        # Depending on security policy, either 403 or 404 can be returned.
        # 404 can prevent leaking information about existing tracking numbers.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, # Or status.HTTP_403_FORBIDDEN
            detail="Shipment not found or not authorized.",
        )
    return shipment

@router.patch("/{shipment_id}/status", response_model=schemas.ShipmentRead)
async def update_shipment_status_endpoint(
    shipment_id: uuid.UUID,
    status_update: schemas.ShipmentStatusUpdate,
    db_session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    # Retrieve the shipment by ID
    shipment = await crud_shipment.get_shipment_by_id(
        db_session=db_session, shipment_id=shipment_id
    )

    # Check if shipment exists
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found.",
        )

    # Security Check: Verify ownership
    if shipment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, # Or 404 to obscure existence
            detail="Not authorized to update this shipment's status.",
        )

    # Business Logic: Simplified - allow update to any valid status
    # In a real app, add checks here, e.g., user can only cancel 'pending'

    # Update the shipment status
    updated_shipment = await crud_shipment.update_shipment_status(
        db_session=db_session, 
        shipment_id=shipment_id, 
        new_status=status_update.status.value
    )
    
    if not updated_shipment:
        # This case should ideally be covered by the initial get_shipment_by_id check,
        # but as a safeguard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found during update.",
        )
        
    return updated_shipment
