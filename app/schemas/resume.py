from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class ResumeBase(BaseModel):
    file_name: str = Field(..., description="Original human-readable name of the uploaded document")

# ==========================================
# 📤 Response Resume Schema (Secure & Optimized)
# ==========================================
class ResumeResponse(ResumeBase):
    id: int
    candidate_id: int
    
    # 1. Cloud & Server Agnostic Access URL Integration
    file_url: str = Field(..., description="Public or proxy routing absolute access URL hook for download/preview")
    
    # 2. Security Guard: 'file_path' is deliberately EXCLUDED here 
    # to protect server internal folder structure signatures from being exposed to clients.
    
    uploaded_at: datetime = Field(..., description="Timestamp of when the file was written to disk storage")

    # Note: 'parsed_text' is excluded from this general schema to prevent massive data overhead 
    # during candidate list queries. It can be loaded via a separate detail schema if needed.

    class Config:
        from_attributes = True