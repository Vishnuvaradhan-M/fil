from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core import deps
# from app.core.conflict_detection import validate_ot_availability, validate_ot_slot_overlap  # Commented out
from app.models.room import Room, RoomType
# OTSlot, OTBooking, OTSlotStatus, OTBookingStatus are commented out in models
from app.models.users import User, UserRole
from app.schemas import room as schemas

router = APIRouter()


# ─── Room CRUD ────────────────────────────────────────────

@router.post("/", response_model=schemas.Room)
def create_room(
    *,
    db: Session = Depends(deps.get_db),
    room_in: schemas.RoomCreate,
    current_user: User = Depends(deps.require_role([UserRole.ADMIN])),
) -> Any:
    """
    Create a new room (Admin only).
    """
    # Ensure room_number is unique since it is used as the business identifier
    existing = db.query(Room).filter(Room.room_number == room_in.room_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Room number already exists")

    room = Room(**room_in.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.get("/", response_model=List[schemas.Room])
def read_rooms(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List all rooms.
    """
    rooms = db.query(Room).offset(skip).limit(limit).all()
    return rooms


@router.get("/{room_number}", response_model=schemas.Room)
def get_room(
    room_number: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a room by room number.
    """
    room = db.query(Room).filter(Room.room_number == room_number).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.put("/{room_number}", response_model=schemas.Room)
def update_room(
    *,
    db: Session = Depends(deps.get_db),
    room_number: str,
    room_in: schemas.RoomUpdate,
    current_user: User = Depends(deps.require_role([UserRole.ADMIN])),
) -> Any:
    """
    Update a room by room number (Admin only).
    """
    room = db.query(Room).filter(Room.room_number == room_number).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    update_data = room_in.model_dump(exclude_unset=True)

    # If room_number is being changed, ensure the new number is not already in use
    new_room_number = update_data.get("room_number")
    if new_room_number and new_room_number != room.room_number:
        existing = db.query(Room).filter(Room.room_number == new_room_number).first()
        if existing:
            raise HTTPException(status_code=400, detail="Room number already exists")

    for field, value in update_data.items():
        setattr(room, field, value)

    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_number}")
def delete_room(
    *,
    db: Session = Depends(deps.get_db),
    room_number: str,
    current_user: User = Depends(deps.require_role([UserRole.ADMIN])),
) -> Any:
    """
    Delete a room by room number (Admin only).
    """
    try:
        # Get the room using raw SQL to avoid model field mismatches
        result = db.execute(
            text("SELECT id FROM rooms WHERE room_number = :room_number"),
            {"room_number": room_number}
        ).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Room not found")
        
        room_id = result[0]
        
        # Delete the room using raw SQL
        db.execute(
            text("DELETE FROM rooms WHERE id = :room_id"),
            {"room_id": room_id}
        )
        
        db.commit()
        return {"detail": f"Room {room_number} deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error deleting room {room_number}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete room: {str(e)}"
        )


# ─── OT Slots and Bookings (Temporarily Disabled) ────────────────────────────────────────────
# These endpoints are commented out because the OTSlot and OTBooking models 
# don't match the current database schema. Uncomment and fix once schema is aligned.

# @router.post("/ot-slots", response_model=schemas.OTSlot)
# def create_ot_slot(...): pass

# @router.get("/ot-slots", response_model=List[schemas.OTSlot])
# def list_ot_slots(...): pass

# @router.get("/ot-slots/available", response_model=List[schemas.OTSlot])
# def list_available_ot_slots(...): pass

# @router.post("/ot-bookings", response_model=schemas.OTBooking)
# def book_ot_slot(...): pass

# @router.get("/ot-bookings", response_model=List[schemas.OTBooking])
# def list_ot_bookings(...): pass

# @router.post("/ot-bookings/{booking_id}/approve", response_model=schemas.OTBooking)
# def approve_ot_booking(...): pass

# @router.post("/ot-bookings/{booking_id}/reject", response_model=schemas.OTBooking)
# def reject_ot_booking(...): pass

