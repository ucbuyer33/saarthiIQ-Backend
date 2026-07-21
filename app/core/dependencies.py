from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database import get_db
from app.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM

logger = logging.getLogger(__name__)

# Authentication OAuth2 protocol specification hook
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ==========================================
# Global Auth & Session Guard
# ==========================================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Decodes the bearer token, resolves the identity, and validates the user
    exists and is active. This is a single-role (recruiter) application, so
    no role-based access control is applied here.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError as jwt_error:
        logger.warning(f"Authentication failure: {str(jwt_error)}")
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id) if user_id.isdigit() else User.email == user_id).first()

    if user is None:
        raise credentials_exception

    if hasattr(user, 'is_active') and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated"
        )

    return user
