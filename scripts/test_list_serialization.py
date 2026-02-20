import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.db import SessionLocal
from app.models.appointment import Appointment
from app.schemas.appointment import Appointment as AppointmentSchema
from typing import List
import json
from pydantic import TypeAdapter

db = SessionLocal()
try:
    appointments = db.query(Appointment).limit(10).all()
    print(f"Found {len(appointments)} appointments")
    
    # Try to serialize each one
    schemas_list = []
    for appt in appointments:
        try:
            schema = AppointmentSchema.model_validate(appt)
            schemas_list.append(schema)
        except Exception as e:
            print(f"Failed to serialize appointment {appt.id}: {e}")
            import traceback
            traceback.print_exc()
            break
    
    print(f"Successfully serialized {len(schemas_list)} appointments")
    
    # Try to convert to JSON
    try:
        adapter = TypeAdapter(List[AppointmentSchema])
        json_str = adapter.dump_json([AppointmentSchema.model_validate(a) for a in appointments[:10]])
        print(f"✓ JSON serialization successful! Length: {len(json_str)}")
    except Exception as e:
        print(f"✗ JSON serialization failed: {e}")
        import traceback
        traceback.print_exc()
        
finally:
    db.close()
