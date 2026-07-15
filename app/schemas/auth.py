from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="Full legal name of the employee or recruiter")
    email: EmailStr = Field(..., description="Official enterprise email address")
    
    # 1. Plain Text Password length guard constraint
    password: str = Field(..., min_length=8, max_length=64, description="Raw plain text password string (Min 8 characters required)")
    
    # 2. Flexible Enterprise Roles Allocation Injection
    # Defaults to 'user', but allows explicitly assigning roles during custom registration pipelines
    role: Optional[str] = Field("user", description="System level access tier: admin, recruiter, interviewer, user")

class UserLogin(BaseModel):
    # Field mappings aligned precisely with OAuth2PasswordRequestForm capabilities
    email: EmailStr = Field(..., description="Registered login email reference")
    password: str = Field(..., description="Plain-text verification password")