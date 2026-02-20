from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db import engine, Base
import app.models  # noqa: F401 — ensure all models are registered with Base
from app.auth import router as auth_router
from app.scheduling import router as scheduling_router
from app.rooms import router as rooms_router
from app.shifts import router as shifts_router
from app.users import router as users_router
from app.ml import router as ml_router

# NOTE:
# For Supabase/managed Postgres in production, we avoid calling
# Base.metadata.create_all(bind=engine) on import, since that will crash
# the app if the database is temporarily unavailable.
# Use migrations or run create_all separately instead.

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Backend for hospital workflow automation (non-clinical) with AI/ML foundations.",
    version="0.1.0",
)

# Enable CORS for frontend dev server and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:5175", "http://127.0.0.1:5176"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# All routers mounted under /api/v1
app.include_router(auth_router.router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(users_router.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(scheduling_router.router, prefix=f"{settings.API_V1_STR}/appointments", tags=["appointments"])
app.include_router(rooms_router.router, prefix=f"{settings.API_V1_STR}/rooms", tags=["rooms"])
app.include_router(shifts_router.router, prefix=f"{settings.API_V1_STR}/shifts", tags=["shifts"])
app.include_router(ml_router.router, prefix=f"{settings.API_V1_STR}/ml", tags=["ml"])
from app.health import router as health_router
app.include_router(health_router.router, prefix=settings.API_V1_STR, tags=["health"])


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "Hospital Workflow Backend Running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
