from typing import Optional
from datetime import date, time, datetime

from pydantic import BaseModel, EmailStr, PositiveInt, constr, field_validator

from app.models.appointment import (
    AppointmentStatus,
    AppointmentType,
    PatientGender,
)


class AppointmentBase(BaseModel):
    patient_id: PositiveInt
    doctor_id: PositiveInt

    appointment_date: date
    start_time: time
    end_time: time
    # Patient details: allow optional submission (frontend may supply), defaults applied server-side
    patient_name: Optional[constr(max_length=120)] = None
    patient_phone: Optional[constr(max_length=20)] = None
    patient_email: Optional[EmailStr] = None
    patient_gender: Optional[PatientGender] = None
    patient_age: Optional[PositiveInt] = None

    # Optional room linkage (frontend may provide)
    room_id: Optional[int] = None

    appointment_type: AppointmentType
    reason_for_visit: constr(max_length=255)
    notes: Optional[constr(max_length=500)] = None


class AppointmentCreate(AppointmentBase):
    @field_validator("end_time")
    @classmethod
    def validate_time_order(cls, v: time, info):  # type: ignore[override]
        start = info.data.get("start_time")
        if start is not None and v <= start:
            raise ValueError("end_time must be after start_time")
        return v


class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    patient_name: Optional[constr(max_length=120)] = None
    patient_phone: Optional[constr(max_length=20)] = None
    patient_email: Optional[EmailStr] = None
    patient_gender: Optional[PatientGender] = None
    patient_age: Optional[PositiveInt] = None
    appointment_type: Optional[AppointmentType] = None
    reason_for_visit: Optional[constr(max_length=255)] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[constr(max_length=500)] = None


class AppointmentInDBBase(AppointmentBase):
    id: int
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime
    # Augmented field for responses
    room_name: Optional[str] = None

    class Config:
        from_attributes = True


class Appointment(AppointmentInDBBase):
    pass

class AvailabilityBase(BaseModel):
    doctor_id: PositiveInt
    day_of_week: int
    start_time: time
    end_time: time


class AvailabilityCreate(AvailabilityBase):
    pass


class Availability(AvailabilityBase):
    id: int

    class Config:
        from_attributes = True
