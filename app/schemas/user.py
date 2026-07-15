from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name of the system user or employee")
    email: EmailStr = Field(..., description="Official enterprise authenticated email identity")

# ==========================================
# 📥 User Create Schema (Synchronized with Registration Constraints)
# ==========================================
class UserCreate(UserBase):
    # 1. Strict Plain-Text Password Length Constraints to prevent weak hashes
    password: str = Field(..., min_length=8, max_length=64, description="Raw plain text password string (Min 8 characters required)")
    
    # 2. Advanced Multi-Role Injection Capability
    role: Optional[str] = Field("user", description="System tier authorization level: admin, recruiter, interviewer, user")
    is_active: Optional[bool] = Field(True, description="Allows initializing user activation state explicitly")

# ==========================================
# 📤 User Response Schema (Matches routes/users.py exactly)
# ==========================================
class UserResponse(UserBase):
    id: int
    role: str = Field(..., description="Assigned authorization context status")
    is_active: bool = Field(..., description="Determines if user is banned or active in operational pipelines")
    created_at: datetime

    class Config:
        from_attributes = True