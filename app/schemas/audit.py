from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class AuditResponse(BaseModel):
    id: int
    action: str
    module: str
    user_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AuditListResponse(BaseModel):
    total: int
    page: int
    limit: int
    results: List[AuditResponse]