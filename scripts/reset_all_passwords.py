#!/usr/bin/env python3
"""
Reset all user passwords to valid Argon2 hashes for consistent login.
This fixes the login issue where only 3 users can authenticate.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from app.core.db import SessionLocal
from app.models.users import User
from app.core.security import get_password_hash

db = SessionLocal()

try:
    # Define passwords based on user role
    password_map = {
        'admin': 'admin123',
        'doctor': 'password123',
        'hr': 'password123',
        'staff': 'password123'
    }
    
    users = db.query(User).all()
    print(f"Updating {len(users)} users with valid Argon2 hashes...\n")
    
    updated = 0
    for user in users:
        # Determine password based on role
        role = user.role.value  # Get string value of enum
        password = password_map.get(role, 'password123')
        
        # Update with Argon2 hash
        user.hashed_password = get_password_hash(password)
        updated += 1
        print(f"✅ {user.email:25} ({role:8}) - Password reset")
    
    # Commit all changes
    db.commit()
    
    print(f"\n{'='*70}")
    print(f"✅ Successfully updated {updated} users")
    print(f"{'='*70}")
    print("\nLogin credentials:")
    print("  ADMIN:  admin@hospital.com / admin123")
    print("  DOCTOR: doctor1@hospital.com / password123")
    print("  DOCTOR: doctor2@hospital.com / password123 (etc)")
    print("  HR:     hr1@hospital.com / password123")
    print("  HR:     hr2@hospital.com / password123 (etc)")
    print("  STAFF:  staff1@hospital.com / password123")
    print("  STAFF:  staff2@hospital.com / password123 (etc)")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
