from typing import Optional
from datetime import datetime

from pydantic import BaseModel, PositiveInt, constr, field_validator

from app.models.shift import AssignmentStatus  # Removed ShiftName import as it's not used


class ShiftBase(BaseModel):
    name: Optional[str] = None  # Changed from shift_name to match database
    start_time: datetime  # Changed to datetime to match database TIMESTAMP
    end_time: datetime  # Changed to datetime to match database TIMESTAMP
    type: constr(max_length=9)  # Changed from multiple fields to match database
    # Fields below don't exist in database - removed:
    # shift_date: date
    # department: constr(max_length=80)
    # required_staff_count: PositiveInt

    @field_validator("end_time")
    @classmethod
    def validate_time_order(cls, v: datetime, info):  # type: ignore[override]
        start = info.data.get("start_time")
        if start is not None and v <= start:
            raise ValueError("end_time must be after start_time")
        return v


class ShiftCreate(ShiftBase):
    pass


class ShiftUpdate(BaseModel):
    name: Optional[str] = None  # Changed from shift_name to match database
    start_time: Optional[datetime] = None  # Changed to datetime to match database
    end_time: Optional[datetime] = None  # Changed to datetime to match database
    type: Optional[constr(max_length=9)] = None  # Changed from multiple fields to match database
    # Fields below don't exist in database - removed:
    # shift_date: Optional[date] = None
    # department: Optional[constr(max_length=80)] = None
    # required_staff_count: Optional[PositiveInt] = None

    @field_validator("end_time")
    @classmethod
    def validate_time_order_update(cls, v: Optional[datetime], info):  # type: ignore[override]
        if v is None:
            return v
        start = info.data.get("start_time")
        if start is not None and v <= start:
            raise ValueError("end_time must be after start_time")
        return v


class Shift(ShiftBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShiftAssignmentBase(BaseModel):
    staff_id: PositiveInt
    shift_id: PositiveInt
    status: Optional[str] = "ASSIGNED"  # Database enum values: ASSIGNED, COMPLETED, SWAP_REQUESTED, SWAPPED


class ShiftAssignmentCreate(ShiftAssignmentBase):
    pass


class ShiftAssignment(ShiftAssignmentBase):
    id: int
    target_staff_id: Optional[int] = None  # Actual column name in database
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShiftSwapRequest(BaseModel):
    assignment_id: int
    target_staff_id: int
