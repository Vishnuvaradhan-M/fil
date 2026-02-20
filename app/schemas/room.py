from typing import Optional
from datetime import date, time, datetime

from pydantic import BaseModel, PositiveInt, constr, field_validator

from app.models.room import RoomType
# OTSlotStatus, OTBookingStatus are commented out in models


class RoomBase(BaseModel):
    room_number: constr(max_length=20)
    ward_name: constr(max_length=80)
    room_type: Optional[RoomType] = None
    bed_capacity: PositiveInt
    floor_number: int
    is_active: bool = True


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    room_number: Optional[constr(max_length=20)] = None
    ward_name: Optional[constr(max_length=80)] = None
    room_type: Optional[RoomType] = None
    bed_capacity: Optional[PositiveInt] = None
    floor_number: Optional[int] = None
    is_active: Optional[bool] = None


class Room(RoomBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# NOTE: OT-related schemas are commented out because the models don't match the database schema
# Uncomment and fix these once the database schema is aligned

# class OTSlotBase(BaseModel):
#     room_id: PositiveInt
#     slot_date: date
#     start_time: time
#     end_time: time
#     status: OTSlotStatus = OTSlotStatus.AVAILABLE
#
#     @field_validator("end_time")
#     @classmethod
#     def validate_time_order(cls, v: time, info):  # type: ignore[override]
#         start = info.data.get("start_time")
#         if start is not None and v <= start:
#             raise ValueError("end_time must be after start_time")
#         return v
#
#
# class OTSlotCreate(OTSlotBase):
#     pass
#
#
# class OTSlot(OTSlotBase):
#     id: int
#     created_at: datetime
#     updated_at: datetime
#
#     class Config:
#         from_attributes = True
#
#
# class OTBookingBase(BaseModel):
#     ot_slot_id: PositiveInt
#     booking_reference: constr(max_length=50)
#     doctor_id: PositiveInt
#     department: constr(max_length=80)
#     purpose: constr(max_length=255)
#
#
# class OTBookingCreate(OTBookingBase):
#     pass
#
#
# class OTBooking(OTBookingBase):
#     id: int
#     status: OTBookingStatus
#     approved_by: Optional[int]
#     created_at: datetime
#     updated_at: datetime
#
#     class Config:
#         from_attributes = True

