from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.audit import Audit
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.audit import AuditListResponse

router = APIRouter(prefix="/audit", tags=["Audit Logs"])

@router.get("/", response_model=AuditListResponse, status_code=status.HTTP_200_OK)
async def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    module: Optional[str] = None,
    action: Optional[str] = None,
    user_id: Optional[int] = None,
):
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only administrators can access system logs.",
        )

    query = db.query(Audit)

    if module:
        query = query.filter(Audit.module == module)
    if action:
        query = query.filter(Audit.action == action)
    if user_id:
        query = query.filter(Audit.user_id == user_id)

    total_logs = query.count()
    offset = (page - 1) * limit
    logs = query.order_by(Audit.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "total": total_logs,
        "page": page,
        "limit": limit,
        "results": logs,
    }