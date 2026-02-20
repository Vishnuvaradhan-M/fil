"""
Bootstrap script to create an initial admin user.
Run: python -m scripts.create_admin
Or:  python scripts/create_admin.py
"""
import sys
import os

# Add project root to path so imports work when run as a module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.db.db import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.users import User, UserRole
from sqlalchemy import text


def create_admin():
    """
    (Re)creates the admin user with a fresh password hash.
    Deletes the old admin user if it exists.
    """
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Delete existing admin user using raw SQL to avoid cascade issues
        email_to_delete = settings.FIRST_SUPERUSER_EMAIL
        result = db.execute(
            text(f"DELETE FROM users WHERE email = '{email_to_delete}'")
        )
        db.commit()
        if result.rowcount > 0:
            print(f"Deleted existing admin user: {email_to_delete}")

        # Create the new admin user
        print(f"Creating admin user with email: {settings.FIRST_SUPERUSER_EMAIL}")
        plain_password = settings.FIRST_SUPERUSER_PASSWORD
        print(f"Using plain text password for hashing: '{plain_password}'")
        
        hashed_password = get_password_hash(plain_password)
        print(f"Generated hashed password (first 10 chars): {hashed_password[:10]}...")

        admin = User(
            email=settings.FIRST_SUPERUSER_EMAIL,
            hashed_password=hashed_password,
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print("\nAdmin user created successfully.")
        print(f"  Email:    {settings.FIRST_SUPERUSER_EMAIL}")
        print(f"  Password: {settings.FIRST_SUPERUSER_PASSWORD}")
        print("  Role:     admin")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
