from typing import List, Any
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core import deps
from app.core.conflict_detection import validate_doctor_availability
from app.models.appointment import Appointment, AppointmentStatus, DoctorAvailability
from app.models.users import User, UserRole
from app.schemas import appointment as schemas

router = APIRouter()


@router.post("/", response_model=schemas.Appointment)
def create_appointment(
    *,
    db: Session = Depends(deps.get_db),
    appointment_in: schemas.AppointmentCreate,
    current_user: User = Depends(deps.require_role([UserRole.ADMIN, UserRole.DOCTOR])),
) -> Any:
    """
    Create new appointment (Admin or Doctor only).
    """
    is_available = validate_doctor_availability(
        db,
        appointment_in.doctor_id,
        appointment_in.appointment_date,
        appointment_in.start_time,
        appointment_in.end_time,
    )
    if not is_available:
        raise HTTPException(status_code=400, detail="Doctor is not available at the requested time.")

    # Prevent non-admins from booking in the past (IST)
    today_ist = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    if (
        current_user.role != UserRole.ADMIN
        and appointment_in.appointment_date < today_ist
    ):
        raise HTTPException(status_code=400, detail="Appointment date cannot be in the past.")

    appointment = Appointment(**appointment_in.model_dump())
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("/", response_model=List[schemas.Appointment])
def read_appointments(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve appointments.
    Admin/HR/Staff see all. Doctor sees own. Others get 403.
    """
    if current_user.role == UserRole.ADMIN or current_user.role == UserRole.HR or current_user.role == UserRole.STAFF:
        appointments = db.query(Appointment).offset(skip).limit(limit).all()
    elif current_user.role == UserRole.DOCTOR:
        appointments = db.query(Appointment).filter(
            Appointment.doctor_id == current_user.id
        ).offset(skip).limit(limit).all()
    else:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    return appointments


@router.put("/{appointment_id}", response_model=schemas.Appointment)
def update_appointment(
    *,
    db: Session = Depends(deps.get_db),
    appointment_id: int,
    appointment_in: schemas.AppointmentUpdate,
    current_user: User = Depends(deps.require_role([UserRole.ADMIN, UserRole.DOCTOR])),
) -> Any:
    """
    Update an appointment (Admin or Doctor for own appointment only).
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Doctor can only update own appointments
    if current_user.role == UserRole.DOCTOR and appointment.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your appointment")

    if appointment_in.appointment_date or appointment_in.start_time or appointment_in.end_time:
        new_date = appointment_in.appointment_date or appointment.appointment_date
        new_start = appointment_in.start_time or appointment.start_time
        new_end = appointment_in.end_time or appointment.end_time

        is_available = validate_doctor_availability(
            db,
            appointment.doctor_id,
            new_date,
            new_start,
            new_end,
        )
        if not is_available:
            raise HTTPException(status_code=400, detail="Doctor is not available at the new time.")
        appointment.appointment_date = new_date
        appointment.start_time = new_start
        appointment.end_time = new_end

    update_data = appointment_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in {"appointment_date", "start_time", "end_time"}:
            continue  # already applied above
        setattr(appointment, field, value)

    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.delete("/{appointment_id}", response_model=schemas.Appointment)
def cancel_appointment(
    *,
    db: Session = Depends(deps.get_db),
    appointment_id: int,
    current_user: User = Depends(deps.require_role([UserRole.ADMIN, UserRole.DOCTOR])),
) -> Any:
    """
    Cancel an appointment (soft delete via status change).
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if current_user.role == UserRole.DOCTOR and appointment.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your appointment")

    appointment.status = AppointmentStatus.CANCELLED
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.post("/availability", response_model=schemas.Availability)
def create_availability(
    *,
    db: Session = Depends(deps.get_db),
    availability_in: schemas.AvailabilityCreate,
    current_user: User = Depends(deps.require_role([UserRole.ADMIN, UserRole.DOCTOR])),
) -> Any:
    """
    Set doctor availability.
    """
    availability = DoctorAvailability(**availability_in.model_dump())
    db.add(availability)
    db.commit()
    db.refresh(availability)
    return availability
