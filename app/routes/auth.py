from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
import logging

from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister, db: Session = Depends(get_db)):
    """Registers a new user inside the system securely with role awareness."""
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Allow only safe public roles from registration: "user" (Recrutee) and "recruiter".
    allowed_public_roles = {"user", "recruiter"}
    requested_role = user.role or "user"
    if requested_role not in allowed_public_roles:
        requested_role = "user"  # fallback to Recrutee

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hash_password(user.password),
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
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticates user and returns standard OAuth2 bearer token."""
    db_user = db.query(User).filter(User.email == form_data.username).first()

    # Generic error text for security (Taaki attackers ko pata na chale email query fail hui ya pass)
    invalid_credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Email or Password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not db_user:
        raise invalid_credentials_exception

    # 2. Updated Column Reference Checked
    if not verify_password(form_data.password, db_user.hashed_password):
        raise invalid_credentials_exception

    # 3. Account Status Check (Deactivated users check)
    if hasattr(db_user, 'is_active') and not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Contact admin."
        )

    # 4. Correct Token Call: Explicit 'subject' syntax jo security.py me banaya tha
    token = create_access_token(subject=db_user.email)

    return {
        "access_token": token,
        "token_type": "bearer"
    }
