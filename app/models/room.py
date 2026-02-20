from sqlalchemy import Column, Integer, String, DateTime, Date, Time, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base
import enum


class RoomType(str, enum.Enum):
    GENERAL = "General"
    ICU = "ICU"
    PRIVATE = "Private"
    SEMI_PRIVATE = "SemiPrivate"


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, nullable=False)
    ward_name = Column(String, nullable=False)
    room_type = Column(Enum(RoomType), nullable=False)
    bed_capacity = Column(Integer, nullable=False)
    floor_number = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# NOTE: OTSlot and OTBooking models are commented out because they don't match the database schema
# Uncomment and fix these models once the database schema is aligned

# class OTSlotStatus(str, enum.Enum):
#     AVAILABLE = "Available"
#     BOOKED = "Booked"
#     MAINTENANCE = "Maintenance"
#     BLOCKED = "Blocked"


# class OTSlot(Base):
#     __tablename__ = "ot_slots"
#     id = Column(Integer, primary_key=True, index=True)
#     room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
#     # Add correct columns here based on actual database schema
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# class OTBookingStatus(str, enum.Enum):
#     PENDING = "Pending"
#     APPROVED = "Approved"
#     REJECTED = "Rejected"
#     COMPLETED = "Completed"


# class OTBooking(Base):
#     __tablename__ = "ot_bookings"
#     id = Column(Integer, primary_key=True, index=True)
#     # Add correct columns here based on actual database schema
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
