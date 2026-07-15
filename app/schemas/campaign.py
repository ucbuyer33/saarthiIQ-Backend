from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

# 1. Strict Status Lifecycle Enum for System Consistency
class CampaignStatus(str, Enum):
    SCHEDULED = "Scheduled"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"
    PAUSED = "Paused"

class CampaignBase(BaseModel):
    campaign_name: str = Field(..., min_length=3, max_length=150, description="Name of the recruitment campaign")
    subject: str = Field(..., min_length=5, max_length=255, description="Email subject line line")
    message: str = Field(..., description="Raw text or HTML email body payload content")

# ==========================================
# 📥 Create Campaign Schema
# ==========================================
class CampaignCreate(CampaignBase):
    pass

# ==========================================
# 🔄 Update Campaign Schema (Flexible & Optional)
# ==========================================
class CampaignUpdate(BaseModel):
    # Made everything optional to allow clean partial updates via model_dump(exclude_unset=True)
    campaign_name: Optional[str] = Field(None, min_length=3, max_length=150)
    subject: Optional[str] = Field(None, min_length=5, max_length=255)
    message: Optional[str] = None
    status: Optional[CampaignStatus] = Field(None, description="Updates the execution flow state")

# ==========================================
# 📤 Response Campaign Schema
# ==========================================
class CampaignResponse(CampaignBase):
    id: int
    status: CampaignStatus
    created_by: int
    
    # 2. Analytics Integration Layers (Crucial for background workers telemetry)
    total_recipients: Optional[int] = Field(0, description="Total candidates selected for this batch run")
    sent_count: Optional[int] = Field(0, description="Successfully delivered email operations counter")
    
    created_at: datetime

    class Config:
        from_attributes = True