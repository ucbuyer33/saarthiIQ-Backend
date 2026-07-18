# saarthiIQ-Backend\app\routes\users.py
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.services.audit_service import log_action

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_logged_in_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_current_logged_in_user(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = payload.dict(exclude_unset=True)

    if "email" in data:
        existing = db.query(User).filter(
            User.email == data["email"],
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use."
            )

    for field, value in data.items():
        setattr(current_user, field, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    log_action(
        db,
        action="UPDATE",
        module="profile",
        user_id=current_user.id,
        details={"fields": list(data.keys())},
    )

    return current_user


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can access all users."
        )

    users = db.query(User).order_by(User.id.desc()).all()
    return [
        {
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "role": u.role,
            "created_at": u.created_at,
        }
        for u in users
    ]