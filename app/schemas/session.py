# saarthiIQ-Backend\app\schemas\session.py
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

class SessionResponse(BaseModel):
    id: int
    user_id: int
    device_name: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_current: bool
    created_at: datetime
    last_active: datetime
    location: Optional[str] = None

    class Config:
        from_attributes = True

class SessionListResponse(BaseModel):
    data: List[SessionResponse]