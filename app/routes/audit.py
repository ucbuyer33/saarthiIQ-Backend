from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from app.database import get_db
from app.models.audit import Audit
from app.models.user import User
from app.core.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/audit",
    tags=["Audit Logs"]
)

# 1. async def aur safe response handling
@router.get("/", status_code=status.HTTP_200_OK)
async def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    # 2. Advanced Dynamic Filtering & Pagination
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Logs per page"),
    module: Optional[str] = Query(None, description="Filter by module (e.g., auth, candidate)"),
    action: Optional[str] = Query(None, description="Filter by action (e.g., CREATE, DELETE)"),
    user_id: Optional[int] = Query(None, description="Filter by specific user ID")
):
    """
    Fetches system audit logs with pagination and multi-filters. 
    Strictly restricted to Admin role.
    """
    
    # 3. Critical Security Check: Only Admins can view audit trails
    if hasattr(current_user, 'role') and current_user.role != "admin":
        logger.warning(f"Unauthorized audit log access attempt by user ID: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only administrators can access system logs."
        )

    # Base Query construction
    query = db.query(Audit)

    # Apply dynamic filters if provided
    if module:
        query = query.filter(Audit.module == module)[cite: 1]
    if action:
        query = query.filter(Audit.action == action)[cite: 1]
    if user_id:
        query = query.filter(Audit.user_id == user_id)[cite: 1]

    # Calculate offset for pagination
    offset = (page - 1) * limit
    
    # Get total count before slicing (useful for frontend pagination bars)
    total_logs = query.count()

    # Fetch ordered chunk of data safely
    logs = query.order_by(Audit.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "total": total_logs,
        "page": page,
        "limit": limit,
        "results": logs
    }