import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.db import SessionLocal
from app.models.appointment import Appointment
from app.schemas.appointment import Appointment as AppointmentSchema

db = SessionLocal()
try:
    appt = db.query(Appointment).first()
    if appt:
        print(f"Found appointment: {appt.id}")
        print(f"Appointment attributes: {vars(appt)}")
        
        try:
            schema = AppointmentSchema.model_validate(appt)
            print(f"✓ Serialization successful!")
            print(f"Schema dict: {schema.model_dump()}")
        except Exception as e:
            print(f"✗ Serialization failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("No appointments found")
finally:
    db.close()
