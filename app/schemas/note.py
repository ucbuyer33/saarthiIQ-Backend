from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class NoteBase(BaseModel):
    # Empty strings aur unreasonable payloads se bachne ke liye range validation lagayi
    note: str = Field(..., min_length=2, max_length=2000, description="Internal evaluation remarks or interviewer feedback notes")

# ==========================================
# 📥 Create Note Schema
# ==========================================
class NoteCreate(NoteBase):
    pass

# ==========================================
# 🔄 Update Note Schema (Crucial for Route Compilation!)
# ==========================================
class NoteUpdate(NoteBase):
    """Used in PUT /notes/{note_id} to validate revised remarks."""
    pass

# ==========================================
# 📤 Response Note Schema
# ==========================================
class NoteResponse(NoteBase):
    id: int
    candidate_id: int
    created_by: int
    
    created_at: datetime
    # 2. Syncing with database model timestamps to track edits seamlessly
    updated_at: Optional[datetime] = Field(None, description="Timestamp of the latest modification if edited")

    class Config:
        from_attributes = True