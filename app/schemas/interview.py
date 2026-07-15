from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

# 1. Strict Interview Round Status Lifecycle Enum
class InterviewStatus(str, Enum):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    REJECTED = "Rejected"
    CANCELLED = "Cancelled"

class InterviewBase(BaseModel):
    interview_type: str = Field(..., description="Round type (e.g., Technical, HR Screening, System Design)")
    interview_date: datetime = Field(..., description="Timezone aware scheduling timestamp matrix")
    
    # Optional dynamic parameter addition for online meetings
    meeting_link: Optional[str] = Field(None, description="Direct URL hook for Google Meet / Zoom call sync")

# ==========================================
# 📥 Create Interview Schema
# ==========================================
class InterviewCreate(InterviewBase):
    # 2. Advanced Multi-Type Interviewer Mapping Sync
    interviewer_id: Optional[int] = Field(None, description="Linked system Internal User account ID reference")
    interviewer_name: str = Field(..., min_length=2, max_length=100, description="Raw name string fallback representation")

# ==========================================
# 🔄 Update Interview Schema (Highly Flexible for Rescheduling & Feedback)
# ==========================================
class InterviewUpdate(BaseModel):
    # Made completely optional to facilitate smooth partial updates or custom rescheduling loops
    interview_type: Optional[str] = None
    interview_date: Optional[datetime] = None
    meeting_link: Optional[str] = None
    status: Optional[InterviewStatus] = Field(None, description="Transitions the round lifecycle status safely")
    feedback: Optional[str] = Field(None, description="Detailed score evaluations or final interview summary notes")

# ==========================================
# 📤 Response Interview Schema
# ==========================================
class InterviewResponse(InterviewBase):
    id: int
    candidate_id: int
    
    # Reflects the system structural schema changes cleanly
    interviewer_id: Optional[int] = None
    interviewer_name: str
    
    status: InterviewStatus
    feedback: Optional[str] = None

    class Config:
        from_attributes = True