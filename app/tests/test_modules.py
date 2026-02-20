import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from datetime import datetime, timedelta
from app.core.conflict_detection import check_time_overlap, validate_doctor_availability, validate_shift_overlap  # validate_ot_availability commented out
from app.core.db import SessionLocal, Base, engine
from app.models.users import User, UserRole
from app.models.appointment import Appointment, AppointmentStatus, DoctorAvailability
from app.models.room import Room, RoomType  # OTSlot, OTSlotStatus commented out
from app.models.shift import Shift, StaffShiftAssignment, ShiftType

def test_conflict_detection_logic():
    print("Testing Conflict Logic...")
    start1 = datetime(2023, 10, 27, 10, 0)
    end1 = datetime(2023, 10, 27, 11, 0)
    
    # Overlapping
    assert check_time_overlap(start1, end1, datetime(2023, 10, 27, 10, 30), datetime(2023, 10, 27, 11, 30)) == True
    # Non-overlapping
    assert check_time_overlap(start1, end1, datetime(2023, 10, 27, 11, 0), datetime(2023, 10, 27, 12, 0)) == False # Edge touch is usually not overlap depending on strictness, but here < min(end) implies strict.
    
    print("Conflict logic passed.")

def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    return db

def teardown_db(db):
    db.close()

def test_modules_integration():
    db = setup_db()
    try:
        print("Testing DB Integration...")
        
        # Create Users
        doctor = User(email="doc@test.com", hashed_password="pw", full_name="Dr Test", role=UserRole.DOCTOR, is_active=True)
        admin = User(email="admin@test.com", hashed_password="pw", full_name="Admin", role=UserRole.ADMIN, is_active=True)
        staff = User(email="staff@test.com", hashed_password="pw", full_name="Nurse", role=UserRole.STAFF, is_active=True)
        db.add_all([doctor, admin, staff])
        db.commit()
        
        # 1. Doctor Availability & Appointment
        # Set availability: Mon 9-5
        avail = DoctorAvailability(doctor_id=doctor.id, day_of_week=0, start_time=datetime.strptime("09:00", "%H:%M").time(), end_time=datetime.strptime("17:00", "%H:%M").time())
        db.add(avail)
        db.commit()
        
        # Try to book appointment within slot
        appt_start = datetime(2023, 10, 30, 10, 0) # Mon
        appt_end = datetime(2023, 10, 30, 11, 0)
        
        # Check logic directly first
        assert validate_doctor_availability(db, doctor.id, appt_start, appt_end) == True
        
        # Create appointment
        appt = Appointment(patient_id=1, doctor_id=doctor.id, start_time=appt_start, end_time=appt_end, status=AppointmentStatus.SCHEDULED)
        db.add(appt)
        db.commit()
        
        # Try to book overlap
        assert validate_doctor_availability(db, doctor.id, datetime(2023, 10, 30, 10, 30), datetime(2023, 10, 30, 11, 30)) == False
        print("Doctor availability verification passed.")
        
        # 2. Room & OT
        room = Room(name="OT-1", type=RoomType.OT)
        db.add(room)
        db.commit()
        
        slot = OTSlot(room_id=room.id, start_time=appt_start, end_time=appt_end, status=OTSlotStatus.AVAILABLE)
        db.add(slot)
        db.commit()
        
        assert validate_ot_availability(db, slot.id) == True
        # Mark booked (simulating booking)
        slot.status = OTSlotStatus.BOOKED
        db.commit()
        assert validate_ot_availability(db, slot.id) == False
        print("OT availability verification passed.")

        # 3. Shifts
        shift = Shift(name="Morning", start_time=appt_start, end_time=appt_end, type=ShiftType.MORNING)
        db.add(shift)
        db.commit()
        
        assign = StaffShiftAssignment(staff_id=staff.id, shift_id=shift.id)
        db.add(assign)
        db.commit()
        
        # Validate overlap
        assert validate_shift_overlap(db, staff.id, appt_start, appt_end) == False # False means invalid/overlapping? Wait, logic: function check_time_overlap returns True if overlap.
        # Function name is validate_shift_overlap.
        # My implementation:
        # returns False if overlap found (invalid), True if valid (no overlap)?
        # Let's check logic:
        # validate_shift_overlap returns False if there IS an overlap.
        # "if check_time_overlap(...): return False"
        
        assert validate_shift_overlap(db, staff.id, datetime(2023, 10, 30, 12, 0), datetime(2023, 10, 30, 13, 0)) == True # valid
        assert validate_shift_overlap(db, staff.id, datetime(2023, 10, 30, 10, 30), datetime(2023, 10, 30, 11, 30)) == False # invalid, overlap
        
        print("Shift overlap verification passed.")
        
    finally:
        teardown_db(db)

if __name__ == "__main__":
    test_conflict_detection_logic()
    test_modules_integration()
