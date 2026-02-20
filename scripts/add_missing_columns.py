"""
Add missing columns to database for refactored ML system.
Adds: doctor_name to doctor_availability, assignment_date to staff_shift_assignments
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.db import SessionLocal

def add_missing_columns():
    """Add doctor_name and assignment_date columns"""
    db = SessionLocal()
    
    try:
        print("="*60)
        print("DATABASE SCHEMA MIGRATION")
        print("="*60)
        
        # Add doctor_name column to doctor_availability
        print("\n1. Adding doctor_name to doctor_availability...")
        try:
            db.execute(text("""
                ALTER TABLE doctor_availability 
                ADD COLUMN IF NOT EXISTS doctor_name VARCHAR(100);
            """))
            db.commit()
            print("   ✅ Column doctor_name added")
        except Exception as e:
            print(f"   ℹ️  Column may already exist: {e}")
            db.rollback()
        
        # Add assignment_date column to staff_shift_assignments
        print("\n2. Adding assignment_date to staff_shift_assignments...")
        try:
            db.execute(text("""
                ALTER TABLE staff_shift_assignments 
                ADD COLUMN IF NOT EXISTS assignment_date DATE;
            """))
            db.commit()
            print("   ✅ Column assignment_date added")
        except Exception as e:
            print(f"   ℹ️  Column may already exist: {e}")
            db.rollback()
        
        # Update doctor_name from users table
        print("\n3. Populating doctor_name from users...")
        result = db.execute(text("""
            UPDATE doctor_availability da
            SET doctor_name = CONCAT('Dr. ', u.full_name)
            FROM users u
            WHERE da.doctor_id = u.id 
            AND da.doctor_name IS NULL;
        """))
        db.commit()
        print(f"   ✅ Updated {result.rowcount} records")
        
        # Update assignment_date from shifts
        print("\n4. Populating assignment_date from shifts...")
        result = db.execute(text("""
            UPDATE staff_shift_assignments ssa
            SET assignment_date = s.date
            FROM shifts s
            WHERE ssa.shift_id = s.id 
            AND ssa.assignment_date IS NULL;
        """))
        db.commit()
        print(f"   ✅ Updated {result.rowcount} records")
        
        print("\n" + "="*60)
        print("✅ MIGRATION COMPLETE")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_missing_columns()
