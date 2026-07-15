from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.dashboard_service import get_dashboard_data

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# 1. async def use kiya concurrency issues ko fix karne ke liye
@router.get("/", status_code=status.HTTP_200_OK)
async def get_user_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetches real-time workspace dashboard statistics tailored to the current user's security level.
    """
    try:
        # 2. Scope Injection: Pass current_user to isolate metrics based on user.role
        dashboard_stats = get_dashboard_data(db=db, user=current_user)
        
        if dashboard_stats is None:
            return {
                "summary": "No active workflow data found.",
                "metrics": {}
            }
            
        return dashboard_stats

    except Exception as e:
        logger.error(f"Failed to compile dashboard metrics for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while preparing your dashboard data."
        )