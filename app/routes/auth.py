from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
import logging

from app.database import get_db
from app.models.user import User
from app.models.session import UserSession
from app.schemas.auth import UserRegister
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.session import SessionResponse, SessionListResponse
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_session_token,
)
from app.core.dependencies import get_current_user
from app.services.audit_service import log_action
from app.utils.id_gen import generate_user_id          # ← NEW

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

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
    db.flush()   # ← assigns new_user.id (PK) without committing

    # ── Generate role-prefixed Feistel ID now that we have the PK ────────────
    new_user.user_id = generate_user_id(new_user.id, requested_role)
    # ─────────────────────────────────────────────────────────────────────────

    log_action(
        db, "REGISTER", "auth",
        user_id=new_user.id,
        details={"email": new_user.email, "role": new_user.role, "user_id": new_user.user_id},
    )
    db.commit()
    db.refresh(new_user)

    return {
        "status":  "success",
        "message": "User Registered Successfully",
        "user_id": new_user.user_id,   # ← now returns "CD001423" style
        "db_id":   new_user.id,
        "email":   new_user.email,
        "role":    new_user.role,
    }


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
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
    if hasattr(db_user, "is_active") and not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Contact admin.",
        )

    token         = create_access_token(subject=db_user.email, role=db_user.role)
    session_token = create_session_token()

    device_name = "Desktop Browser"
    ua = request.headers.get("user-agent", "")
    if ua:
        low = ua.lower()
        if any(x in low for x in ["iphone", "android", "mobile", "ipad"]):
            device_name = "Mobile Device"
    try:
        session = UserSession(
            user_id=db_user.id,
            session_token=session_token,
            device_name=device_name,
            ip_address=request.client.host if request.client else None,
            user_agent=ua,
            is_current=True,
        )
        db.add(session)
        log_action(db, "LOGIN", "auth", user_id=db_user.id, details={"email": db_user.email, "device": device_name})
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "access_token":  token,
        "token_type":    "bearer",
        "session_token": session_token,
    }


@router.get("/sessions", response_model=SessionListResponse, status_code=status.HTTP_200_OK)
async def get_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = (
        db.query(UserSession)
        .filter(UserSession.user_id == current_user.id)
        .order_by(UserSession.created_at.desc())
        .all()
    )
    return {"data": sessions}


@router.delete("/sessions/{session_id}", status_code=status.HTTP_200_OK)
async def revoke_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id,
    ).first()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    db.delete(session)
    log_action(db, "REVOKE_SESSION", "auth", user_id=current_user.id, details={"session_id": session_id})
    db.commit()
    return {"status": "success", "message": "Session revoked"}


@router.post("/logout-everywhere", status_code=status.HTTP_200_OK)
async def logout_everywhere(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(UserSession).filter(UserSession.user_id == current_user.id).delete()
    log_action(db, "LOGOUT_EVERYWHERE", "auth", user_id=current_user.id)
    db.commit()
    return {"status": "success", "message": "Logged out everywhere"}


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_password = payload.get("current_password", "")
    new_password     = payload.get("new_password", "")
    if not current_password or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password and new password are required",
        )
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    current_user.hashed_password = get_password_hash(new_password)
    db.add(current_user)
    log_action(db, "PASSWORD_CHANGE", "auth", user_id=current_user.id)
    db.commit()
    return {"status": "success", "message": "Password updated"}


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.id
    db.delete(current_user)
    log_action(db, "DELETE", "auth", user_id=user_id)
    db.commit()
    return {"status": "success", "message": "Account deleted"}


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = payload.dict(exclude_unset=True)

    if "email" in data:
        existing = db.query(User).filter(
            User.email == data["email"],
            User.id != current_user.id,
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use.",
            )

    for field, value in data.items():
        setattr(current_user, field, value)

    db.add(current_user)
    log_action(db, "UPDATE", "profile", user_id=current_user.id, details={"fields": list(data.keys())})
    db.commit()
    db.refresh(current_user)
    return current_user
