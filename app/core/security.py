# saarthiIQ-Backend\app\core\security.py
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Any
import uuid  # 👈 Added for session token generation
from jose import jwt
from passlib.context import CryptContext
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Password hashing configuration matrix
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=12  # CPU complexity controls for production safety
)

# Configs validation mappings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def get_password_hash(password: str) -> str:
    """Hashes a plain text password using bcrypt. (Synced for app routers)"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against its hash with timing leak guards."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password encryption mismatch verification failure: {str(e)}")
        return False

def create_access_token(subject: Union[str, Any], role: str = "user", expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a secure, time-bounded JWT access token.
    Properly encodes subject and dynamic authorization roles mapping fields.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Payload claims structure containing scope definitions array
    to_encode = {
        "sub": str(subject),
        "role": str(role),  # Injected seamlessly to match RoleChecker loops in dependencies.py
        "exp": expire,
        "iss": "SaarthiIQ-Core-Engine"  # Issuing authority tracker tag
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_session_token() -> str:
    """Generates a secure, unique random string token for sessions."""
    return str(uuid.uuid4())
