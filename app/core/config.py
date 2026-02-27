from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


# Ensure the backend/.env file is always loaded, regardless of cwd.
_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_ENV_PATH = os.path.join(_BASE_DIR, ".env")
# Load .env into environment but avoid leaking optional subsystem keys (like GROQ_API_KEY)
# which can cause validation errors in Settings when unknown variables are present.
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

    # Pydantic v2 model config: allow extra env vars so optional subsystem envs don't break startup
    model_config = {"extra": "ignore", "case_sensitive": True, "env_file": ".env"}


# Temporarily remove GROQ_API_KEY from os.environ during core settings instantiation
_groq_key = os.environ.pop("GROQ_API_KEY", None)
try:
    settings = Settings()
finally:
    if _groq_key is not None:
        os.environ["GROQ_API_KEY"] = _groq_key
