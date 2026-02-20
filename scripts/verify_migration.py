
import sys
import os
from sqlalchemy import text

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from app.core.config import settings
    from app.core.db import engine
    
    db_url = settings.DATABASE_URL
    if "@" in db_url:
        print(f"Testing connection to: {db_url.split('@')[-1]}")
    else:
        print(f"Testing connection to: {db_url}")
    
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Successfully connected to Supabase!")
        print(f"Query Result: {result.fetchone()}")
        
except Exception as e:
    import traceback
    with open("verify_error.log", "w") as f:
        traceback.print_exc(file=f)
        f.write(str(e))
    sys.exit(1)
