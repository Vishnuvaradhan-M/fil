
import sys
import os
sys.path.append(os.getcwd())
from app.core.config import settings

print("--- Loaded Settings (Masked) ---")
print(f"DATABASE_URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'NOT LOADED'}")
print(f"API_V1_STR: {settings.API_V1_STR}")
print(f"PROJECT_NAME: {settings.PROJECT_NAME}")
