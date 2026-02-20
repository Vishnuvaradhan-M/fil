import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.db import SessionLocal
from app.models.room import Room
from app.schemas.room import Room as RoomSchema

db = SessionLocal()
try:
    rooms = db.query(Room).all()
    print(f"Found {len(rooms)} rooms")
    
    for room in rooms:
        try:
            schema = RoomSchema.model_validate(room)
            print(f"✓ Room {room.id}: {room.room_number} OK")
        except Exception as e:
            print(f"✗ Room {room.id} serialization failed: {e}")
            print(f"  Room data: {vars(room)}")
            import traceback
            traceback.print_exc()
            break
            
finally:
    db.close()
