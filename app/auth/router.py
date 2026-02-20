from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core import deps
from app.core.config import settings
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.users import User, UserRole
from app.schemas.users import Token, UserCreate, User as UserSchema

router = APIRouter()


@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """OAuth2 compatible token login. Get an access token for future requests."""
    try:
        user = db.query(User).filter(User.email == form_data.username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": create_access_token(
                subject=user.email, expires_delta=access_token_expires, role=user.role.value
            ),
            "token_type": "bearer",
        }
    except HTTPException:
        # Propagate expected auth errors as-is
        raise
    except Exception as exc:  # noqa: BLE001
        # Surface the underlying error message to help diagnose 500s
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {exc!r}",
        )


@router.post("/register", response_model=UserSchema)
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.require_role([UserRole.ADMIN])),
) -> Any:
    """
    Register a new user (Admin only).
    """
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=user_in.is_active if user_in.is_active is not None else True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
