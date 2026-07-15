from pydantic import BaseModel, Field
from typing import Dict, Any

class CandidateStatusMetrics(BaseModel):
    # Breakdown structure to support visual pipeline charts (Pie/Bar charts)
    Applied: int = Field(0, description="Counter for candidates in initial screening stage")
    Interviewing: int = Field(0, description="Counter for candidates with active schedule rounds")
    Shortlisted: int = Field(0, description="Counter for successfully qualified pipeline candidates")
    Rejected: int = Field(0, description="Counter for archiving profile records")

class DashboardStats(BaseModel):
    # Core system global/isolated numerical metrics
    total_candidates: int = Field(0, description="Total profiles matching user tenancy scope")
    total_users: int = Field(0, description="Total system internal team accounts")
    total_interviews: int = Field(0, description="Total scheduled interview cycles context")
    total_tasks: int = Field(0, description="Active reminders/tasks count assigned to user")
    total_campaigns: int = Field(0, description="Total continuous bulk email tracks spawned")

    # Advanced Analytics Matrix Addition
    candidate_status_breakdown: CandidateStatusMetrics = Field(
        default_factory=CandidateStatusMetrics, 
        description="Categorized pipeline stage distributions for data visualization cards"
    )

    class Config:
        from_attributes = True