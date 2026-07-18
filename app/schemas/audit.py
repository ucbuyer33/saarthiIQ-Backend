from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class AuditResponse(BaseModel):
    id: int
    action: str = Field(..., description="Event action type")
    module: str = Field(..., description="System module")
    user_id: Optional[int] = Field(None, description="User who performed the action")
    details: Optional[Dict[str, Any]] = Field(None, description="Extra metadata")
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(..., description="Timestamp")

    class Config:
        from_attributes = True