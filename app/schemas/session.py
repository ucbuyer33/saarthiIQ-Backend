from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class SessionResponse(BaseModel):
    id: int
    user_id: int
    device_name: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_current: bool
    created_at: datetime
    last_active: datetime

    class Config:
        from_attributes = True