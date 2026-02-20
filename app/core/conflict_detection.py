from datetime import datetime, date, time
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.appointment import Appointment, AppointmentStatus, DoctorAvailability
# from app.models.room import OTSlot, OTBooking, OTSlotStatus  # Commented out until schema aligned
from app.models.shift import Shift, StaffShiftAssignment, AssignmentStatus

def check_time_overlap(start1: time, end1: time, start2: time, end2: time) -> bool:
    """
    Returns True if the time ranges overlap.
    """
    return max(start1, start2) < min(end1, end2)

def validate_doctor_availability(
    db: Session,
    doctor_id: int,
    appointment_date: date,
    start_time: time,
    end_time: time,
) -> bool:
    """
    Validates if a doctor is available:
    1. Checks if the time slot is within their working hours (DoctorAvailability).
    2. Checks if they have any overlapping appointments.
    Returns True if available, False otherwise.
    """
    # 1. Check working hours (simplified: assumes weekly schedule)
    day_of_week = appointment_date.weekday()  # 0=Monday
    availability = db.query(DoctorAvailability).filter(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.day_of_week == day_of_week
    ).first()

    if not availability:
        # If no availability defined, assume unavailable or default? 
        # Requirement says "Availability validation before booking". 
        # If not defined, let's assume valid for now OR invalid. Safe bet: Invalid if not explicitly available.
        return False
    
    # Check time boundaries (all values are plain times in IST)
    if start_time < availability.start_time or end_time > availability.end_time:
        return False

    # 2. Check existing appointments
    overlap = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appointment_date,
        Appointment.status == AppointmentStatus.SCHEDULED,
        or_(
            and_(Appointment.start_time < end_time, Appointment.start_time >= start_time),
            and_(Appointment.end_time > start_time, Appointment.end_time <= end_time),
            and_(Appointment.start_time <= start_time, Appointment.end_time >= end_time),
        ),
    ).first()

    if overlap:
        return False

    return True


# NOTE: OT-related validation functions commented out until OT models are fixed
# def validate_ot_availability(db: Session, ot_slot_id: int) -> bool:
#     """Checks if an OT slot is available for booking."""
#     slot = db.query(OTSlot).filter(OTSlot.id == ot_slot_id).first()
#     if not slot or slot.status != OTSlotStatus.AVAILABLE:
#         return False
#
#     # Check if already booked (non-cancelled/non-rejected bookings)
#     booking = db.query(OTBooking).filter(OTBooking.ot_slot_id == ot_slot_id).first()
#     if booking:
#         return False
#
#     return True
#
#
# def validate_ot_slot_overlap(
#     db: Session,
#     room_id: int,
#     slot_date: date,
#     start_time: time,
#     end_time: time,
# ) -> bool:
#     """Ensure no overlapping OT slots exist for a room on a given date."""
#     existing_slots = db.query(OTSlot).filter(
#         OTSlot.room_id == room_id,
#         OTSlot.slot_date == slot_date,
#     ).all()
#
#     for slot in existing_slots:
#         if check_time_overlap(start_time, end_time, slot.start_time, slot.end_time):
#             return False
#
#     return True


def validate_shift_overlap(
    db: Session,
    staff_id: int,
    shift_date: date,
    start_time: time,
    end_time: time,
) -> bool:
    """Checks if a staff member already has an overlapping shift on the same date."""
    from app.models.shift import Shift
    
    assignments = db.query(StaffShiftAssignment).filter(
        StaffShiftAssignment.staff_id == staff_id,
        StaffShiftAssignment.assignment_status.in_([AssignmentStatus.ASSIGNED, AssignmentStatus.SWAPPED]),
    ).all()

    for assignment in assignments:
        # Get shift directly since relationship is commented out
        shift = db.query(Shift).filter(Shift.id == assignment.shift_id).first()
        if not shift or shift.shift_date != shift_date:
            continue
        if check_time_overlap(start_time, end_time, shift.start_time, shift.end_time):
            return False

    return True
