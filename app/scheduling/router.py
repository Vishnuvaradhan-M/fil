from typing import List, Any
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
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
    # Fill missing patient details with safe defaults if frontend did not provide them
    data = appointment_in.model_dump()
    if not data.get("patient_name"):
        data["patient_name"] = "Unknown"
    if not data.get("patient_phone"):
        data["patient_phone"] = ""
    if not data.get("patient_age"):
        data["patient_age"] = 0
    if not data.get("patient_gender"):
        data["patient_gender"] = "Other"
    # Fill missing appointment fields with defaults
    if not data.get("appointment_type"):
        data["appointment_type"] = schemas.AppointmentType.CONSULTATION.value
    if not data.get("reason_for_visit"):
        data["reason_for_visit"] = "Not provided"

    # Rebuild appointment_in from data to include defaults
    appointment_in = schemas.AppointmentCreate(**data)

    # Enforce availability only for non-admin users; admins may schedule regardless.
    if current_user.role != UserRole.ADMIN:
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

    # Only include room_id if the appointments table has the column defined
    data = appointment_in.model_dump()
    if "room_id" not in Appointment.__table__.columns:
        data.pop("room_id", None)
    appointment = Appointment(**data)
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
    # Check if appointments table actually has a room_id column before attempting SQL join
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        has_room_id = "room_id" in [c["name"] for c in inspector.get_columns("appointments")]
    except Exception:
        has_room_id = False

    try:
        if has_room_id:
            # Use raw SQL to fetch appointments with optional room_name if room linkage exists.
            if current_user.role in {UserRole.ADMIN, UserRole.HR, UserRole.STAFF}:
                sql = """
                    SELECT a.*, r.ward_name as room_name
                    FROM appointments a
                    LEFT JOIN rooms r ON a.room_id = r.id
                    ORDER BY a.id
                    LIMIT :limit OFFSET :skip
                """
                rows = db.execute(text(sql), {"limit": limit, "skip": skip}).mappings().all()
            elif current_user.role == UserRole.DOCTOR:
                sql = """
                    SELECT a.*, r.ward_name as room_name
                    FROM appointments a
                    LEFT JOIN rooms r ON a.room_id = r.id
                    WHERE a.doctor_id = :doctor_id
                    ORDER BY a.id
                    LIMIT :limit OFFSET :skip
                """
                rows = db.execute(text(sql), {"limit": limit, "skip": skip, "doctor_id": current_user.id}).mappings().all()
            else:
                raise HTTPException(status_code=403, detail="Not enough privileges")
            # Map rows to dictionaries and return; response_model will validate
            result = []
            for r in rows:
                d = dict(r)
                result.append(d)
            return result
        # else fall through to ORM-based retrieval
        if current_user.role not in {UserRole.ADMIN, UserRole.HR, UserRole.STAFF, UserRole.DOCTOR}:
            raise HTTPException(status_code=403, detail="Not enough privileges")

        # Map rows to dictionaries and return; response_model will validate
        result = []
        for r in rows:
            d = dict(r)
            # Ensure enums are converted to expected types for Pydantic
            result.append(d)
        return result
    except Exception:
        # Raw SQL failed (likely schema mismatch such as missing room_id) — rollback and fallback to ORM
        try:
            db.rollback()
        except Exception:
            pass
        if current_user.role in {UserRole.ADMIN, UserRole.HR, UserRole.STAFF}:
            appointments = db.query(Appointment).offset(skip).limit(limit).all()
        elif current_user.role == UserRole.DOCTOR:
            appointments = db.query(Appointment).filter(
                Appointment.doctor_id == current_user.id
            ).offset(skip).limit(limit).all()
        else:
            raise HTTPException(status_code=403, detail="Not enough privileges")
        # Build response list with optional room_name if available
        out = []
        for a in appointments:
            d = {
                "id": a.id,
                "patient_id": a.patient_id,
                "doctor_id": a.doctor_id,
                "appointment_date": a.appointment_date,
                "start_time": a.start_time,
                "end_time": a.end_time,
                "patient_name": a.patient_name,
                "patient_phone": a.patient_phone,
                "patient_email": a.patient_email,
                "patient_gender": a.patient_gender,
                "patient_age": a.patient_age,
                "appointment_type": a.appointment_type,
                "status": a.status,
                "reason_for_visit": a.reason_for_visit,
                "notes": a.notes,
                "created_at": a.created_at,
                "updated_at": a.updated_at,
                "room_name": None,
            }
            try:
                if hasattr(a, "room") and a.room is not None:
                    d["room_name"] = getattr(a.room, "ward_name", None)
            except Exception:
                d["room_name"] = None
            out.append(d)
        return out


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
