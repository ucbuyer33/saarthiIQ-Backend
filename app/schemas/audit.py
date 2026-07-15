from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class AuditResponse(BaseModel):
    id: int
    action: str = Field(..., description="The event action type (e.g., CREATE, UPDATE, DELETE)")
    module: str = Field(..., description="System area where change occurred (e.g., auth, candidate)")
    
    # 1. Nullability Protection: If a system cron or public hook triggers an audit log
    user_id: Optional[int] = Field(None, description="The ID of the user who performed the action, if applicable")
    
    # 2. Dynamic Payload Capture: JSON logs metadata for front-end insights
    details: Optional[Dict[str, Any]] = Field(None, description="Detailed JSON metadata or context about the operational change")
    
    created_at: datetime = Field(..., description="Timestamp of when the audit log was recorded")

    class Config:
        # Pydantic v2 compatible ORM attribute mapping mode
        from_attributes = True