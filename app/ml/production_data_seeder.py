# app/ml/production_data_seeder.py
"""
Production-grade data seeder for ML training.
Creates 14,000+ realistic appointments with proper distributions.
"""

import random
from datetime import datetime, timedelta, time, date
from sqlalchemy import text
from app.core.db import SessionLocal
from app.core.security import get_password_hash
from app.models.users import User, UserRole
from app.models.appointment import Appointment, DoctorAvailability
from app.models.room import Room
from app.models.shift import Shift, StaffShiftAssignment, AssignmentStatus, ShiftName


# Realistic data pools
MALE_NAMES = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles"]
FEMALE_NAMES = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"]
LASTNAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
             "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

DEPARTMENTS = ["General", "Emergency", "ICU", "Cardiology", "Pediatrics", "Orthopedics"]
SHIFT_TYPES = ["Morning", "Evening", "Night"]

CONSULTATION_REASONS = [
    "Annual checkup", "Follow-up visit", "Prescription refill", "Lab results review",
    "Chronic disease management", "Preventive care", "Vaccination", "Health screening"
]
EMERGENCY_REASONS = [
    "Chest pain", "Severe abdominal pain", "High fever", "Difficulty breathing",
    "Head injury", "Severe bleeding", "Allergic reaction", "Heart palpitations"
]


def truncate_all_tables(db):
    """Truncate all data tables (preserve schema)."""
    print("Truncating existing data...")
    
    try:
        # Disable foreign key checks temporarily
        db.execute(text("SET CONSTRAINTS ALL DEFERRED"))
        
        # Truncate in correct order (respecting foreign keys)
        tables = [
            "staff_shift_assignments",
            "appointments",
            "shifts",
            "rooms",
            "doctor_availability",
            "users"
        ]
        
        for table in tables:
            db.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
            print(f"  ✓ Truncated {table}")
        
        db.commit()
        print("✅ All tables truncated\n")
    except Exception as e:
        db.rollback()
        print(f"❌ Error truncating tables: {e}")
        raise


def seed_users(db):
    """Create realistic users with varied demographics."""
    print("Seeding users...")
    
    users = []
    
    # 1 Admin
    users.append(User(
        email="admin@hospital.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Hospital Administrator",
        role=UserRole.ADMIN,
        is_active=True
    ))
    
    # 2 HR
    for i in range(2):
        name = random.choice(FEMALE_NAMES if i % 2 == 0 else MALE_NAMES)
        users.append(User(
            email=f"hr{i+1}@hospital.com",
            hashed_password=get_password_hash("password123"),
            full_name=f"{name} {random.choice(LASTNAMES)}",
            role=UserRole.HR,
            is_active=True
        ))
    
    # 8 Doctors
    doctor_names = []
    for i in range(8):
        gender = random.choice(["Male", "Female"])
        name = random.choice(MALE_NAMES if gender == "Male" else FEMALE_NAMES)
        full_name = f"Dr. {name} {random.choice(LASTNAMES)}"
        doctor_names.append(full_name)
        
        users.append(User(
            email=f"doctor{i+1}@hospital.com",
            hashed_password=get_password_hash("password123"),
            full_name=full_name,
            role=UserRole.DOCTOR,
            is_active=True
        ))
    
    # 15 Staff/Nurses
    for i in range(15):
        gender = random.choice(["Male", "Female"])
        name = random.choice(MALE_NAMES if gender == "Male" else FEMALE_NAMES)
        
        users.append(User(
            email=f"staff{i+1}@hospital.com",
            hashed_password=get_password_hash("password123"),
            full_name=f"{name} {random.choice(LASTNAMES)}",
            role=UserRole.STAFF,
            is_active=True
        ))
    
    db.add_all(users)
    db.commit()
    
    print(f"  ✓ Created {len(users)} users (1 admin, 2 HR, 8 doctors, 15 staff)")
    return users


def seed_doctor_availability(db, doctors):
    """Create realistic doctor schedules."""
    print("Seeding doctor availability...")
    
    availabilities = []
    
    for doctor in doctors:
        if doctor.role != UserRole.DOCTOR:
            continue
        
        # Each doctor works 4-6 days per week
        working_days = random.sample(range(5), random.randint(4, 5))  # Weekdays mostly
        
        for day in working_days:
            # Morning shift: 8 AM - 1 PM
            availabilities.append(DoctorAvailability(
                doctor_id=doctor.id,
                day_of_week=day,
                start_time=time(8, 0),
                end_time=time(13, 0)
            ))
            
            # Afternoon shift: 2 PM - 7 PM
            if random.random() > 0.3:  # 70% work afternoons too
                availabilities.append(DoctorAvailability(
                    doctor_id=doctor.id,
                    day_of_week=day,
                    start_time=time(14, 0),
                    end_time=time(19, 0)
                ))
    
    db.add_all(availabilities)
    db.commit()
    
    print(f"  ✓ Created {len(availabilities)} doctor availability slots\n")
    return availabilities


def seed_rooms(db):
    """Create hospital rooms."""
    print("Seeding rooms...")
    
    rooms = [
        Room(room_number="G101", ward_name="General", bed_capacity=2, floor_number=1, is_active=True),
        Room(room_number="G102", ward_name="General", bed_capacity=2, floor_number=1, is_active=True),
        Room(room_number="G201", ward_name="General", bed_capacity=4, floor_number=2, is_active=True),
        Room(room_number="ICU01", ward_name="ICU", bed_capacity=1, floor_number=3, is_active=True),
        Room(room_number="ICU02", ward_name="ICU", bed_capacity=1, floor_number=3, is_active=True),
        Room(room_number="P301", ward_name="Private", bed_capacity=1, floor_number=3, is_active=True),
        Room(room_number="P302", ward_name="Private", bed_capacity=1, floor_number=3, is_active=True),
    ]
    
    db.add_all(rooms)
    db.commit()
    
    print(f"  ✓ Created {len(rooms)} rooms\n")
    return rooms


def seed_shifts(db):
    """Create shifts for last 120 days."""
    print("Seeding shifts...")
    
    shifts = []
    base_date = datetime.now() - timedelta(days=120)
    
    for day in range(120):
        current_date = base_date + timedelta(days=day)
        
        # Morning shift: 8 AM - 4 PM
        shifts.append(Shift(
            name="Morning",
            start_time=datetime.combine(current_date.date(), time(8, 0)),
            end_time=datetime.combine(current_date.date(), time(16, 0)),
            type=ShiftName.MORNING
        ))
        
        # Afternoon shift: 4 PM - 12 AM
        shifts.append(Shift(
            name="Afternoon",
            start_time=datetime.combine(current_date.date(), time(16, 0)),
            end_time=datetime.combine(current_date.date(), time(23, 59)),
            type=ShiftName.AFTERNOON
        ))
        
        # Night shift: 12 AM - 8 AM
        shifts.append(Shift(
            name="Night",
            start_time=datetime.combine(current_date.date(), time(0, 0)),
            end_time=datetime.combine(current_date.date(), time(8, 0)),
            type=ShiftName.NIGHT
        ))
    
    db.add_all(shifts)
    db.commit()
    
    print(f"  ✓ Created {len(shifts)} shifts\n")
    return shifts


def seed_staff_assignments(db, shifts, staff):
    """Assign staff to shifts with varied workload."""
    print("Seeding staff shift assignments...")
    
    assignments = []
    staff_list = [s for s in staff if s.role == UserRole.STAFF]
    
    for shift in shifts:
        # Randomly assign 2-4 staff per shift
        assigned_count = random.randint(2, 4)
        selected_staff = random.sample(staff_list, min(assigned_count, len(staff_list)))
        
        for person in selected_staff:
            assignments.append(StaffShiftAssignment(
                shift_id=shift.id,
                staff_id=person.id
            ))
    
    db.add_all(assignments)
    db.commit()
    
    print(f"  ✓ Created {len(assignments)} staff assignments\n")


def seed_appointments(db, doctors):
    """Create 14,000+ realistic appointments."""
    print("Seeding appointments (this may take a minute)...")
    
    doctor_list = [d for d in doctors if d.role == UserRole.DOCTOR]
    if not doctor_list:
        print("  ❌ No doctors found!")
        return
    
    appointments = []
    base_date = datetime.now() - timedelta(days=120)
    patient_id_counter = 1000
    
    for day in range(120):
        current_date = base_date + timedelta(days=day)
        
        # Weekday vs weekend
        is_weekend = current_date.weekday() >= 5
        
        # Appointments per day: 100-150 on weekdays, 50-80 on weekends
        daily_appointments = random.randint(50, 80) if is_weekend else random.randint(100, 150)
        
        for _ in range(daily_appointments):
            # Random hour: 8 AM - 7 PM (most activity)
            hour = random.choices(
                range(8, 20),
                weights=[5, 8, 10, 12, 15, 14, 12, 10, 8, 6, 5, 4],  # Peak at 2-3 PM
                k=1
            )[0]
            
            start_hour = hour
            start_minute = random.choice([0, 15, 30, 45])
            end_hour = start_hour if start_minute < 45 else start_hour + 1
            end_minute = (start_minute + 30) % 60 if start_minute < 45 else 0
            
            # Patient demographics
            patient_age = int(random.gauss(45, 20))  # Normal distribution around 45
            patient_age = max(5, min(95, patient_age))  # Clamp to 5-95
            
            patient_gender = random.choice(["Male", "Female"])
            patient_name = f"{random.choice(MALE_NAMES if patient_gender == 'Male' else FEMALE_NAMES)} {random.choice(LASTNAMES)}"
            
            # 15-20% emergencies
            is_emergency = random.random() < 0.175
            appointment_type = "Emergency" if is_emergency else "Consultation"
            reason = random.choice(EMERGENCY_REASONS if is_emergency else CONSULTATION_REASONS)
            
            appointments.append(Appointment(
                patient_id=patient_id_counter,
                doctor_id=random.choice(doctor_list).id,
                appointment_date=current_date.date(),
                start_time=time(start_hour, start_minute),
                end_time=time(end_hour, end_minute),
                patient_name=patient_name,
                patient_phone=f"555-{random.randint(1000, 9999)}",
                patient_gender=patient_gender,
                patient_age=patient_age,
                appointment_type=appointment_type,
                status="Completed",
                reason_for_visit=reason
            ))
            
            patient_id_counter += 1
            
            # Batch commit every 1000 appointments
            if len(appointments) % 1000 == 0:
                db.add_all(appointments)
                db.commit()
                print(f"  ✓ Committed {len(appointments)} appointments...")
                appointments = []
    
    # Commit remaining
    if appointments:
        db.add_all(appointments)
        db.commit()
    
    total_count = db.query(Appointment).count()
    print(f"  ✓ Created {total_count} total appointments\n")


def run_full_seed():
    """Execute complete database seeding."""
    print("="*60)
    print("PRODUCTION DATA SEEDER - ML Training Dataset")
    print("="*60 + "\n")
    
    db = SessionLocal()
    
    try:
        # Step 1: Truncate
        truncate_all_tables(db)
        
        # Step 2: Seed users
        users = seed_users(db)
        doctors = [u for u in users if u.role == UserRole.DOCTOR]
        staff = [u for u in users if u.role == UserRole.STAFF]
        
        # Step 3: Seed doctor availability
        seed_doctor_availability(db, doctors)
        
        # Step 4: Seed rooms
        seed_rooms(db)
        
        # Step 5: Seed shifts
        shifts = seed_shifts(db)
        
        # Step 6: Seed staff assignments
        seed_staff_assignments(db, shifts, staff)
        
        # Step 7: Seed appointments (MOST IMPORTANT)
        seed_appointments(db, users)
        
        print("="*60)
        print("✅ DATABASE SEEDING COMPLETE")
        print("="*60)
        print("\nFinal counts:")
        print(f"  Users: {db.query(User).count()}")
        print(f"  Doctor Availability: {db.query(DoctorAvailability).count()}")
        print(f"  Rooms: {db.query(Room).count()}")
        print(f"  Shifts: {db.query(Shift).count()}")
        print(f"  Staff Assignments: {db.query(StaffShiftAssignment).count()}")
        print(f"  Appointments: {db.query(Appointment).count()}")
        print("\n✅ Ready for ML training!")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_full_seed()
