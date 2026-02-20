"""Compatibility layer that re-exports the central DB objects.

All code should go through this module, but the actual engine
configuration lives in app.db.db so there is a single source of truth.
"""

from app.db.db import engine, SessionLocal, Base, get_db  # noqa: F401

