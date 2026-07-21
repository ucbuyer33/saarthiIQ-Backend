from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="Full legal name of the recruiter")
    email: EmailStr = Field(..., description="Official enterprise email address")
    password: str = Field(..., min_length=8, max_length=64, description="Raw plain text password string (Min 8 characters required)")

class UserLogin(BaseModel):
    # Field mappings aligned precisely with OAuth2PasswordRequestForm capabilities
    email: EmailStr = Field(..., description="Registered login email reference")
    password: str = Field(..., description="Plain-text verification password")
