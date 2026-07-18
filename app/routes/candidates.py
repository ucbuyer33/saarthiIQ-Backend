# saarthiIQ-Backend\app\routes\candidates.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.services.audit_service import log_action
import logging

from app.database import get_db
from app.models.candidate import Candidate
from app.models.user import User
from app.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateListResponse,
)
from app.core.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"]
)


# ==========================
# 🎯 Create Candidate
# ==========================
@router.post("/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate: CandidateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Critical Crash Guard: Check if email already registered
    existing_candidate = db.query(Candidate).filter(Candidate.email == candidate.email).first()
    if existing_candidate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A candidate with this email address already exists."
        )

    # 2. Schema Safe Mapping: Auto dumps Pydantic dict into SQLAlchemy model
    # Upgraded from .dict() to Pydantic v2 .model_dump()
    new_candidate = Candidate(
        **candidate.model_dump(),  # Perfectly maps with the updated JSON format skills!
        created_by=current_user.id
    )

    db.add(new_candidate)
    log_action(db, "CREATE", "candidate", user_id=current_user.id, details={"candidate_id": new_candidate.id, "email": new_candidate.email})
    db.commit()
    db.refresh(new_candidate)
    return new_candidate


# ==========================
# 📊 Get All Candidates (Paginated & Filtered)
# ==========================
@router.get("/", response_model=CandidateListResponse)
async def get_all_candidates(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by candidate status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Candidate)

    # Multi-tenancy Isolation: Normal users see their own candidates; Admins see all
    if hasattr(current_user, 'role') and current_user.role != "admin":
        query = query.filter(Candidate.created_by == current_user.id)

    # Apply Optional Filters
    if status_filter:
        query = query.filter(Candidate.status == status_filter)

    total_count = query.count()
    offset = (page - 1) * limit
    candidates = query.order_by(Candidate.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "total": total_count,
        "page": page,
        "limit": limit,
        "results": candidates
    }


# ==========================
# 🔍 Get Candidate By ID
# ==========================
@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate_by_id(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    # Access Security Guard
    if candidate.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this profile")

    return candidate


# ==========================
# 🛠️ Update Candidate
# ==========================
@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: int,
    updated_candidate: CandidateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    if candidate.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this profile")

    # 3. Dynamic Field Mapping (Saves partial data cleanly without erasing defaults)
    # Upgraded from .dict() to Pydantic v2 .model_dump()
    update_data = updated_candidate.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(candidate, key, value)
    log_action(db, "UPDATE", "candidate", user_id=current_user.id, details={"candidate_id": candidate.id, "fields": list(update_data.keys())})
    db.commit()
    db.refresh(candidate)
    return candidate


# ==========================
# 🗑️ Delete Candidate
# ==========================
@router.delete("/{candidate_id}", status_code=status.HTTP_200_OK)
async def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    if candidate.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this profile")

    db.delete(candidate)
    log_action(db, "DELETE", "candidate", user_id=current_user.id, details={"candidate_id": candidate.id})
    db.commit()

    return {"message": "Candidate and all associated data deleted successfully"}
