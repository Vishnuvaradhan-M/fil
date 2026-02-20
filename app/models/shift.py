from sqlalchemy import Column, Integer, String, DateTime, Date, Time, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base
import enum


class ShiftName(str, enum.Enum):
    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"
    NIGHT = "NIGHT"


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)  # Changed from shift_name to match database
    start_time = Column(DateTime, nullable=False)  # Changed to DateTime to match database TIMESTAMP
    end_time = Column(DateTime, nullable=False)  # Changed to DateTime to match database TIMESTAMP
    type = Column(Enum(ShiftName, name='shifttype'), nullable=False)  # Use existing PostgreSQL enum
    # Fields below don't exist in database - commented out:
    # shift_date = Column(Date, nullable=False)
    # department = Column(String, nullable=False)
    # required_staff_count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships commented out to avoid loading non-existent columns
    # assignments = relationship("StaffShiftAssignment", back_populates="shift")


class AssignmentStatus(str, enum.Enum):
    """Match the database enum 'shiftassignmentstatus' exactly."""
    ASSIGNED = "ASSIGNED"
    COMPLETED = "COMPLETED"
    SWAP_REQUESTED = "SWAP_REQUESTED"
    SWAPPED = "SWAPPED"


class StaffShiftAssignment(Base):
    __tablename__ = "staff_shift_assignments"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(AssignmentStatus, name='shiftassignmentstatus'), default=AssignmentStatus.ASSIGNED, nullable=True)
    target_staff_id = Column(Integer, nullable=True)  # Actual column name in DB (not swap_requested_to)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships commented out to avoid loading issues
    # staff = relationship("User", foreign_keys=[staff_id])
    # swap_target = relationship("User", foreign_keys=[target_staff_id])
    # shift = relationship("Shift", back_populates="assignments")
