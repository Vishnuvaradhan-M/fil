"""Minimal Supabase Session Pooler connectivity test.

Run with:
    python -m scripts.supabase_smoke_test

This script only tests the database connection using SQLAlchemy
and does not import FastAPI or the main app.
"""

import os
import sys

# Ensure project root is on sys.path when run as a module from backend/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine, text
from app.core.config import settings


def main() -> None:
    print("Using DATABASE_URL:", settings.DATABASE_URL)

    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        connect_args={"sslmode": "require", "connect_timeout": 10},
    )

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            value = result.scalar()
            if value == 1:
                print("✅ Supabase Session Pooler connection successful (SELECT 1)")
            else:
                print("❌ Unexpected result from SELECT 1:", value)
    except Exception as exc:  # noqa: BLE001
        print("❌ Supabase connection failed:", repr(exc))
        raise


if __name__ == "__main__":
    main()
