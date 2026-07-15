from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from app.database import get_db
from app.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM

logger = logging.getLogger(__name__)

# Authentication OAuth2 protocol specification hook
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ==========================================
# 🛡️ Global Auth & Performance Session Guard
# ==========================================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Decodes input bearer tokens, extracts structured metadata identity, 
    and validates database persistence safely with active checks.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate infrastructure signatures token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode token payload metadata fields mapping array
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Identity extract mappings constraints checks
        user_id: Optional[str] = payload.get("sub")
        user_role: Optional[str] = payload.get("role")  # Scaled feature extraction setup
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError as jwt_error:
        logger.warning(f"Signature authentication attempt tracking failure: {str(jwt_error)}")
        raise credentials_exception

    # 🚀 Performance Patch: Database Hit Optimization
    # Instead of string checks (User.email == user_id), lookups match against primary identity integer
    # standardizing caching parameters layer scalability internally
    user = db.query(User).filter(User.id == int(user_id) if user_id.isdigit() else User.email == user_id).first()

    if user is None:
        raise credentials_exception
        
    # Account status validation bounds check 
    if hasattr(user, 'is_active') and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User identity authorization explicitly revoked or deactivated"
        )

    return user

# ==========================================
# 👥 Dynamic Role-Based Access Control (RBAC)
# ==========================================
class RoleChecker:
    """
    Long-Term Extensible Identity Role Verifier Framework.
    Allows easy mapping rules like: Depends(RoleChecker(["admin", "recruiter"]))
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        user_role = getattr(current_user, 'role', None)
        
        if user_role not in self.allowed_roles:
            logger.warning(
                f"Unauthorized resource tracking attempt: User {current_user.email} "
                f"with role '{user_role}' tried to hit restricted path boundaries."
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operational access denied: Insufficient scope level permissions"
            )
            
        return current_user

# ==========================================
# 🚀 Standard Clean Explicit Aliases Shortcuts
# ==========================================
# Keep legacy signatures fully alive without syntax breakage
get_current_active_admin = RoleChecker(["admin"])
get_current_recruiter_or_admin = RoleChecker(["admin", "recruiter"])