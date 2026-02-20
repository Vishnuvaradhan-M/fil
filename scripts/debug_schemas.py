import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + ".."))

from sqlalchemy import inspect
from app.models.appointment import Appointment
from app.models.room import Room

print("Appointment columns:")
for col in inspect(Appointment).columns:
    print(f"  {col.name}: {col.type}")

print("\nRoom columns:")
for col in inspect(Room).columns:
    print(f"  {col.name}: {col.type}")
