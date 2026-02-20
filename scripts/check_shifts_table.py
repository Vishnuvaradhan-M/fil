"""Check if shifts table exists and show its structure"""
import sys
from sqlalchemy import text, inspect
from app.core.db import SessionLocal

def check_shifts_table():
    db = SessionLocal()
    try:
        # Check if table exists
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        print(f"All tables in database: {tables}")
        print()
        
        if 'shifts' in tables:
            print("✓ 'shifts' table EXISTS")
            print("\nColumns in 'shifts' table:")
            columns = inspector.get_columns('shifts')
            for col in columns:
                print(f"  - {col['name']}: {col['type']} (nullable={col['nullable']})")
        else:
            print("✗ 'shifts' table DOES NOT EXIST")
            
        print("\nAttempting to query shifts table...")
        result = db.execute(text("SELECT * FROM shifts LIMIT 1;"))
        print("✓ Query successful!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_shifts_table()
