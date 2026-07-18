# saarthiIQ-Backend\app\routes\tasks.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.services.audit_service import log_action
import logging

from app.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate
from app.core.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


# ==========================================
# 🎯 Create Task
# ==========================================
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates a new task. Relies on model_dump to map parameters safely."""
    # check if assignment user exists if required by business logic
    new_task = Task(
        **data.model_dump(),
        # Agar models me 'created_by' add kiya hai toh link kar sakte ho, 
        # filhal strictly schema properties map ki hain.
    )

    db.add(new_task)
    log_action(db, "CREATE", "task", user_id=current_user.id, details={"task_id": new_task.id})
    db.commit()
    db.refresh(new_task)
    return new_task


# ==========================================
# 📊 Get Tasks (Paginated & Ownership Isolated)
# ==========================================
@router.get("/", status_code=status.HTTP_200_OK)
async def get_my_tasks(
    page: int = Query(1, ge=1, description="Page number index"),
    limit: int = Query(20, ge=1, le=100, description="Items per frame window"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by task status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches tasks. Normal users can only see tasks assigned to them; Admins see all."""
    query = db.query(Task)

    # 1. Multi-Tenancy Boundary Isolation Check
    if hasattr(current_user, 'role') and current_user.role != "admin":
        query = query.filter(Task.assigned_to == current_user.id)

    # Apply Optional Filters
    if status_filter:
        query = query.filter(Task.status == status_filter)

    total_tasks = query.count()
    offset = (page - 1) * limit
    tasks = query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "total": total_tasks,
        "page": page,
        "limit": limit,
        "results": tasks
    }


# ==========================================
# 🔍 Get Task By ID
# ==========================================
@router.get("/{task_id}", status_code=status.HTTP_200_OK)
async def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # 2. Access Security Guard
    if task.assigned_to != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access denied. You are not authorized to view this task description."
        )

    return task


# ==========================================
# 🛠️ Update Task (Partial Safe updates)
# ==========================================
@router.put("/{task_id}", status_code=status.HTTP_200_OK)
async def update_task_details(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # 3. Ownership Edit Guard
    if task.assigned_to != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Unauthorized request. Cannot modify tasks assigned to other accounts."
        )

    # Model Dump Strategy optimized from your layout
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    log_action(db, "UPDATE", "task", user_id=current_user.id, details={"task_id": task.id, "fields": list(update_data.keys())})
    db.commit()
    db.refresh(task)
    return task


# ==========================================
# 🗑️ Delete Task
# ==========================================
@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task_record(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # 4. Final Security Guard
    if task.assigned_to != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Action restricted. You cannot purge this task resource."
        )

    db.delete(task)
    log_action(db, "DELETE", "task", user_id=current_user.id, details={"task_id": task.id})
    db.commit()
    return {"message": "Task deleted successfully"}