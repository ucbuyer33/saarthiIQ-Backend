from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

# 1. Enterprise Task Status Machine Enum
class TaskStatus(str, Enum):
    TODO = "Todo"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ARCHIVED = "Archived"

# 2. Strict Priority Levels Choice Enum 
class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class TaskBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200, description="Brief action title for the recruiter task")
    description: Optional[str] = Field(None, max_length=2000, description="Detailed actionable context checklist metadata")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task triage tracking urgency tier")
    due_date: Optional[datetime] = Field(None, description="Timezone aware tracking execution deadline")
    assigned_to: int = Field(..., description="Target system User account ID internal foreign key link")

# ==========================================
# 📥 Create Task Schema
# ==========================================
class TaskCreate(TaskBase):
    # Restricts injection, defaults state seamlessly upon workspace registration loops
    status: Optional[TaskStatus] = Field(TaskStatus.TODO, description="Initial dashboard stage assignment entry")

# ==========================================
# 🔄 Update Task Schema (Fully Flexible Partial Form Modifier)
# ==========================================
class TaskUpdate(BaseModel):
    # Completely optional framework elements supporting pure model_dump patch updates
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None

# ==========================================
# 📤 Response Task Schema
# ==========================================
class TaskResponse(TaskBase):
    id: int
    status: TaskStatus
    created_at: datetime
    # Note: If your migration models tracker contains updated_at column, link it here:
    # updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True