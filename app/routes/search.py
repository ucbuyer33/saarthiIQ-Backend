from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from app.database import get_db
from app.models.user import User
from app.models.candidate import Candidate
from app.core.dependencies import get_current_user
from app.services.search_service import search_candidates

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/search",
    tags=["Candidate Search"]
)


# 1. Turned to async def and added standard status codes
@router.get("/", status_code=status.HTTP_200_OK)
async def search_system_candidates(
    # Query parameters with clear documentation
    name: Optional[str] = Query(None, description="Search by candidate name (partial match)"),
    email: Optional[str] = Query(None, description="Exact or partial email match"),
    location: Optional[str] = Query(None, description="Filter by city or location"),
    
    # 2. Advanced Feature: Filter by specific tech skills
    skills: Optional[List[str]] = Query(None, description="Filter candidates by specific skills list"),
    
    # 3. Pagination Guards
    page: int = Query(1, ge=1, description="Page index"),
    limit: int = Query(20, ge=1, le=100, description="Items limit per window"),
    
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Advanced candidate search engine supporting text matching, location filters, 
    and structured JSON skill matching with tenancy safety.
    """
    try:
        # 4. Data Protection & Service Injection:
        # DB filters service layer par trigger karne se pehle current_user pass kiya 
        # taaki service file ensure kare ki recruiter sirf apne ya admin sabhi ke documents filter kare.
        search_results = search_candidates(
            db=db,
            user=current_user,
            name=name,
            email=email,
            location=location,
            skills=skills,
            page=page,
            limit=limit
        )
        
        return search_results

    except Exception as e:
        logger.error(f"Search index execution failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while compiling query matching results."
        )