import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas, crud
from app.core.security import get_current_active_user
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=schemas.SupportTicketRead, status_code=status.HTTP_201_CREATED)
async def create_support_ticket_endpoint(
    ticket_in: schemas.SupportTicketCreate,
    db_session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    ticket = await crud.crud_support_ticket.create_support_ticket(
        db_session=db_session, ticket_in=ticket_in, user_id=current_user.id
    )
    return ticket

@router.get("/", response_model=List[schemas.SupportTicketRead])
async def get_my_support_tickets_endpoint(
    db_session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    tickets = await crud.crud_support_ticket.get_support_tickets_by_user(
        db_session=db_session, user_id=current_user.id
    )
    return tickets

@router.get("/{ticket_id}", response_model=schemas.SupportTicketRead)
async def get_support_ticket_by_id_endpoint(
    ticket_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    ticket = await crud.crud_support_ticket.get_support_ticket_by_id(
        db_session=db_session, ticket_id=ticket_id
    )
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support ticket not found.",
        )
    if ticket.user_id != current_user.id: # Add admin check if needed
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this support ticket.",
        )
    return ticket

@router.patch("/{ticket_id}", response_model=schemas.SupportTicketRead)
async def update_support_ticket_status_endpoint(
    ticket_id: uuid.UUID,
    ticket_update: schemas.SupportTicketUpdate,
    db_session: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    ticket = await crud.crud_support_ticket.get_support_ticket_by_id(
        db_session=db_session, ticket_id=ticket_id
    )
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support ticket not found.",
        )
    
    # Authorization: User must own the ticket or be an admin (admin check not implemented)
    # For now, only owner can update. A real app might allow admins to change status too.
    if ticket.user_id != current_user.id: 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this support ticket.",
        )
    
    # Business logic: e.g., users might only be able to change status to "closed"
    # Admins might have more freedom. For now, simple status update.
    updated_ticket = await crud.crud_support_ticket.update_support_ticket_status(
        db_session=db_session, ticket_id=ticket_id, status=ticket_update.status
    )
    if not updated_ticket: # Should not happen if previous check passed
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support ticket not found during update.",
        )
    return updated_ticket
