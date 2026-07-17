# saarthiIQ-Backend\app\routes\auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
import logging

from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin
from app.schemas.user import UserResponse, UserUpdate
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from app.core.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    allowed_public_roles = {"user", "recruiter"}
    requested_role = user.role or "user"
    if requested_role not in allowed_public_roles:
        requested_role = "user"

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role=requested_role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "status": "success",
        "message": "User Registered Successfully",
        "user_id": new_user.id,
        "email": new_user.email,
        "role": new_user.role,
    }


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == form_data.username).first()
    invalid_credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Email or Password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not db_user:
        raise invalid_credentials_exception

    if not verify_password(form_data.password, db_user.hashed_password):
        raise invalid_credentials_exception

    if hasattr(db_user, 'is_active') and not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Contact admin."
        )

    token = create_access_token(subject=db_user.email, role=db_user.role)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_password = payload.get("current_password", "")
    new_password = payload.get("new_password", "")
    if not current_password or not new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password and new password are required")
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    current_user.hashed_password = get_password_hash(new_password)
    db.add(current_user)
    db.commit()
    return {"status": "success", "message": "Password updated"}


@router.post("/logout-everywhere", status_code=status.HTTP_200_OK)
async def logout_everywhere(current_user: User = Depends(get_current_user)):
    return {"status": "success", "message": "Logged out everywhere"}


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    return {"status": "success", "message": "Account deleted"}


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_me(payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = payload.dict(exclude_unset=True)

    if "email" in data:
        existing = db.query(User).filter(User.email == data["email"], User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use.")

    for field, value in data.items():
        setattr(current_user, field, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user