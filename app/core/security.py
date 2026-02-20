from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Support verifying both bcrypt and argon2 password hashes to remain compatible
# with existing databases. Prefer bcrypt for new hashes.
pwd_context = CryptContext(schemes=["bcrypt", "argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against the stored hash.
    Tries the configured CryptContext first; if that fails and argon2-cffi is
    available, fall back to argon2 verification to support legacy hashes.
    """
    try:
        if pwd_context.verify(plain_password, hashed_password):
            return True
    except Exception:
        # Fall through to any fallback checks below
        pass

    # Fallback: try argon2 directly if available (covers environments where
    # passlib couldn't verify but argon2-cffi is installed).
    try:
        from argon2 import PasswordHasher

        ph = PasswordHasher()
        try:
            ph.verify(hashed_password, plain_password)
            return True
        except Exception:
            return False
    except Exception:
        # argon2 not available or verification failed
        return False


def get_password_hash(password: str) -> str:
    # Hash new passwords with the preferred scheme (bcrypt)
    return pwd_context.hash(password)


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None, role: Optional[str] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    if role:
        to_encode["role"] = str(role)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
