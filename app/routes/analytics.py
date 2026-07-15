from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.analytics_service import get_dashboard_stats

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

# 1. async def lagaya taaki high load par server crash na ho
@router.get("/dashboard", status_code=status.HTTP_200_OK)
async def get_dashboard_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetches aggregated dashboard statistics tailored to the user's access level.
    """
    try:
        # 2. Security Context Check & Multi-tenancy Isolation:
        # User object pass kiya taaki service layer filter kar sake ki admin hai ya normal user[cite: 1].
        stats = get_dashboard_stats(db=db, user=current_user)
        
        if stats is None:
            return {
                "total_candidates": 0,
                "active_campaigns": 0,
                "upcoming_interviews": 0,
                "message": "No data available at the moment."
            }
            
        return stats

    except Exception as e:
        logger.error(f"Error fetching analytics for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load dashboard statistics. Please try again later."
        )