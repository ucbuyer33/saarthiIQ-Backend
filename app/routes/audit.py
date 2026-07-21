from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.audit import Audit
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.audit import AuditListResponse

router = APIRouter(prefix="/audit", tags=["Activity Logs"])


@router.get("/", response_model=AuditListResponse, status_code=status.HTTP_200_OK)
async def get_activity_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    module: Optional[str] = None,
    action: Optional[str] = None,
):
    """
    Returns the activity log for the currently authenticated recruiter.
    Each recruiter only sees their own actions.
    """
    query = db.query(Audit).filter(Audit.user_id == current_user.id)

    if module:
        query = query.filter(Audit.module == module)
    if action:
        query = query.filter(Audit.action == action)

    total_logs = query.count()
    offset = (page - 1) * limit
    logs = query.order_by(Audit.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "total": total_logs,
        "page": page,
        "limit": limit,
        "results": logs,
    }
