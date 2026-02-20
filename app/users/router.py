from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core import deps
from app.core.security import get_password_hash
from app.models.users import User, UserRole
from app.schemas.users import User as UserSchema, UserCreate, UserUpdate

router = APIRouter()


@router.post("/register", response_model=UserSchema)
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Public user registration (self-service signup).
    """
    # Check if user already exists
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/", response_model=UserSchema)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.require_role([UserRole.ADMIN, UserRole.HR])),
) -> Any:
    """
    Create a new user (Admin/HR only).
    """
    # Check if user already exists
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/", response_model=List[UserSchema])
def list_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.require_role([UserRole.ADMIN, UserRole.HR])),
) -> Any:
    """
    List all users (Admin/HR only).
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserSchema)
def get_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_role([UserRole.ADMIN])),
) -> Any:
    """
    Get a user by ID (Admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(deps.require_role([UserRole.ADMIN])),
) -> Any:
    """
    Update a user (Admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    else:
        update_data.pop("password", None)

    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}/deactivate", response_model=UserSchema)
def deactivate_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: User = Depends(deps.require_role([UserRole.ADMIN])),
) -> Any:
    """
    Deactivate a user (soft delete via is_active=False). Admin only.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/reset-password/{user_id}", response_model=UserSchema)
def reset_user_password(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    new_password: str = "password123",
    current_user: User = Depends(deps.require_role([UserRole.ADMIN])),
) -> Any:
    """
    Reset a user's password (Admin only). Defaults to 'password123'.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/reset-all-passwords", response_model=dict)
def reset_all_passwords(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_role([UserRole.ADMIN])),
) -> Any:
    """
    Reset all user passwords based on their role (Admin only).
    Used to fix batch authentication issues.
    """
    password_map = {
        UserRole.ADMIN: "admin123",
        UserRole.DOCTOR: "password123",
        UserRole.HR: "password123",
        UserRole.STAFF: "password123",
    }
    
    users = db.query(User).all()
    updated_count = 0
    
    for user in users:
        password = password_map.get(user.role, "password123")
        user.hashed_password = get_password_hash(password)
        updated_count += 1
    
    db.commit()
    
    return {
        "status": "success",
        "updated_count": updated_count,
        "message": f"Reset passwords for {updated_count} users"
    }
