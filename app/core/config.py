from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


# Ensure the backend/.env file is always loaded, regardless of cwd.
_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_ENV_PATH = os.path.join(_BASE_DIR, ".env")
load_dotenv(dotenv_path=_ENV_PATH, override=False)


class Settings(BaseSettings):
    PROJECT_NAME: str = "Hospital Workflow Automation Portal"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    
    # First superuser
    FIRST_SUPERUSER_EMAIL: str = "admin@hospital.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"

    DATABASE_URL: str

    class Config:
        case_sensitive = True
        # env_file kept for compatibility, but load_dotenv above ensures
        # backend/.env is used even when running modules via -m.
        env_file = ".env"


settings = Settings()
