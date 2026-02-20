import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

print(f"DEBUG: SQLALCHEMY_DATABASE_URI type: {type(settings.SQLALCHEMY_DATABASE_URI)}")
print(f"DEBUG: SQLALCHEMY_DATABASE_URI: {settings.SQLALCHEMY_DATABASE_URI}")

# Try connecting
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
try:
    with engine.connect() as connection:
        print("DEBUG: Connection successful!")
except OperationalError as e:
    print(f"DEBUG: Connection failed: {e}")
except Exception as e:
    print(f"DEBUG: Unexpected error: {e}")
