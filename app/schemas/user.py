# saarthiIQ-Backend\app\schemas\user.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    theme: Optional[str] = None
    notification_settings: Optional[str] = None
    email_preferences: Optional[str] = None


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr = Field(...)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=64)
    role: Optional[str] = Field("user")
    is_active: Optional[bool] = Field(True)


class UserResponse(UserBase):
    id: int
    user_id: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    phone: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    theme: Optional[str] = None
    notification_settings: Optional[str] = None
    email_preferences: Optional[str] = None

    candidates_created: Optional[int] = None
    interviews_scheduled: Optional[int] = None
    campaigns_created: Optional[int] = None
    tasks_completed: Optional[int] = None
    last_activity: Optional[datetime] = None

    active_candidates: Optional[int] = None
    resumes_processed: Optional[int] = None
    campaigns_owned: Optional[int] = None
    permission_scope: Optional[str] = None
    admin_privileges: Optional[str] = None
    users_managed: Optional[int] = None

    class Config:
        from_attributes = True