from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from enum import Enum

# ==========================================
# ⚙️ Candidate Pipeline Status States
# ==========================================
class CandidateStatus(str, Enum):
    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    SHORTLISTED = "Shortlisted"
    REJECTED = "Rejected"

# ==========================================
# 📋 Base Candidate Schema
# ==========================================
class CandidateBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name of the candidate")
    email: EmailStr = Field(..., description="Unique email address of the candidate")
    phone: Optional[str] = Field(None, description="Contact phone number")
    
    # 2. Advanced Data Sync: Changed from plain str to structured List[str] 
    # to perfectly handle the database JSON array implementation
    skills: List[str] = Field(default_factory=list, description="List of technical skills extracted or assigned")
    
    experience: Optional[str] = Field(None, description="Experience summary (e.g., '3+ Years')")
    location: Optional[str] = Field(None, description="Current residential city")
    resume_url: Optional[str] = Field(None, description="Absolute pathway link to uploaded resume binary")

# ==========================================
# 📥 Create Candidate Schema
# ==========================================
class CandidateCreate(CandidateBase):
    status: Optional[CandidateStatus] = Field(CandidateStatus.APPLIED, description="Initial hiring tier stage")

# ==========================================
# 🔄 Update Candidate Schema (Highly Flexible)
# ==========================================
class CandidateUpdate(BaseModel):
    # Made completely optional to facilitate smooth partial updates via model_dump(exclude_unset=True)
    full_name: Optional[str] = Field(None, min_length=2, max_length=100, description="Updated full name")
    email: Optional[EmailStr] = Field(None, description="Updated email address")
    phone: Optional[str] = Field(None, description="Updated phone number")
    skills: Optional[List[str]] = Field(None, description="Updated list of technical skills")
    experience: Optional[str] = Field(None, description="Updated experience summary")
    location: Optional[str] = Field(None, description="Updated residential city")
    resume_url: Optional[str] = Field(None, description="Updated pathway link to resume")
    status: Optional[CandidateStatus] = Field(None, description="Updated pipeline status stage")

# ==========================================
# 📤 Response Candidate Schema
# ==========================================
class CandidateResponse(CandidateBase):
    id: int
    status: CandidateStatus
    created_by: int
    created_at: datetime

    # Modern Pydantic v2 configuration format
    model_config = ConfigDict(from_attributes=True)

class CandidateListResponse(BaseModel):
    total: int
    page: int
    limit: int
    results: List[CandidateResponse]
