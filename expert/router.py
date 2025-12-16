# backend/expert/router.py
"""
Expert Connect Router - For farmer-expert consultation requests
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/expert", tags=["Expert Connect"])


class TicketRequest(BaseModel):
    user_id: str
    category: str
    message: str
    image_url: Optional[str] = None


class Ticket(BaseModel):
    id: str
    user_id: str
    category: str
    message: str
    image_url: Optional[str] = None
    status: str
    created_at: str
    updated_at: str


# In-memory storage for demo (replace with database in production)
tickets_db = []


@router.post("/ticket")
async def create_ticket(ticket_request: TicketRequest):
    """
    Create a new expert consultation ticket
    
    Args:
        ticket_request: Ticket details including user_id, category, message
    
    Returns:
        Created ticket with ID and status
    """
    try:
        ticket_id = f"TKT{len(tickets_db) + 1:05d}"
        timestamp = datetime.utcnow().isoformat()
        
        ticket = {
            "id": ticket_id,
            "user_id": ticket_request.user_id,
            "category": ticket_request.category,
            "message": ticket_request.message,
            "image_url": ticket_request.image_url,
            "status": "pending",
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        tickets_db.append(ticket)
        
        logger.info(f"Created expert ticket: {ticket_id} for user: {ticket_request.user_id}")
        
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "ticket": ticket,
                "message": "Expert consultation request submitted successfully"
            }
        )
        
    except Exception as e:
        logger.exception(f"Error creating ticket: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create ticket: {str(e)}"
        )


@router.get("/tickets/{user_id}")
async def get_user_tickets(user_id: str):
    """Get all tickets for a specific user"""
    try:
        user_tickets = [t for t in tickets_db if t["user_id"] == user_id]
        return JSONResponse(content={
            "success": True,
            "tickets": user_tickets,
            "count": len(user_tickets)
        })
    except Exception as e:
        logger.exception(f"Error fetching tickets: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch tickets: {str(e)}"
        )


@router.get("/ticket/{ticket_id}")
async def get_ticket(ticket_id: str):
    """Get specific ticket details"""
    try:
        ticket = next((t for t in tickets_db if t["id"] == ticket_id), None)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return JSONResponse(content={
            "success": True,
            "ticket": ticket
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error fetching ticket: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch ticket: {str(e)}"
        )
