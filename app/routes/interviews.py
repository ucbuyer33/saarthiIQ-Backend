from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db
from app.models.interview import Interview
from app.models.candidate import Candidate
from app.models.user import User
from app.schemas.interview import InterviewCreate, InterviewUpdate
from app.core.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/interviews",
    tags=["Interview Management"]
)

# ==========================================
# 📋 Get All Interviews
# ==========================================
@router.get("", status_code=status.HTTP_200_OK)
async def get_all_interviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch all interviews visible to the current user."""
    query = db.query(Interview)

    if current_user.role != "admin":
        query = query.join(Candidate, Interview.candidate_id == Candidate.id).filter(
            Candidate.created_by == current_user.id
        )

    interviews = query.order_by(Interview.interview_date.desc()).all()

    results = []
    for interview in interviews:
        results.append({
            "id": interview.id,
            "candidate_id": interview.candidate_id,
            "candidate_name": interview.candidate.full_name if interview.candidate else f"Candidate #{interview.candidate_id}",
            "interviewer_name": interview.interviewer_name,
            "interview_type": interview.interview_type,
            "interview_date": interview.interview_date,
            "meeting_link": interview.meeting_link,
            "status": interview.status,
            "feedback": interview.feedback,
        })

    return results


# ==========================================
# 📅 Schedule Interview
# ==========================================
@router.post("/{candidate_id}", status_code=status.HTTP_201_CREATED)
async def schedule_interview(
    candidate_id: int,
    data: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Schedules a new interview round for a candidate with timezone awareness."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Security: Ensure recruiter owns this candidate data context (unless admin)
    if candidate.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to schedule interviews for this candidate."
        )

    # Updated Model Mapping Sync
    new_interview = Interview(
        candidate_id=candidate_id,
        interviewer_id=data.interviewer_id, # Link with registered User ID if provided
        interviewer_name=data.interviewer_name, # Raw string name fallback
        interview_type=data.interview_type,
        interview_date=data.interview_date, # System handles timezone validation via schema
        meeting_link=data.meeting_link if hasattr(data, 'meeting_link') else None,
        status="Scheduled"
    )

    db.add(new_interview)
    
    # Trigger Candidate status update automatically
    candidate.status = "Interviewing"
    
    db.commit()
    db.refresh(new_interview)
    return new_interview


# ==========================================
# 🔍 Get Interviews by Candidate
# ==========================================
@router.get("/{candidate_id}")
async def get_interviews(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches all scheduled or past interview rounds for a specific candidate."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
        
    if candidate.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    return db.query(Interview).filter(Interview.candidate_id == candidate_id).order_by(Interview.interview_date.asc()).all()


# ==========================================
# 🛠️ Update Interview / Feedback / Reschedule
# ==========================================
@router.put("/{interview_id}")
async def update_interview(
    interview_id: int,
    data: InterviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Updates interview state, reschedules or records candidate feedbacks safely."""
    interview = db.query(Interview).filter(Interview.id == interview_id).first()

    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview log not found"
        )

    # Authorization Check (Interviewer or Admin can write feedback)
    if interview.interviewer_id != current_user.id and current_user.role != "admin" and interview.candidate.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permissions to modify this interview session."
        )

    # Safe Dynamic Update Matrix (Handles Rescheduling or Feedback cleanly)
    update_dict = data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(interview, key, value)

    # Automatic Candidate Pipeline Syncer
    if data.status == "Rejected":
        interview.candidate.status = "Rejected"
    elif data.status == "Completed" and interview.candidate.status == "Interviewing":
        # System status reflects evaluation mode
        interview.candidate.status = "Shortlisted" 

    db.commit()
    db.refresh(interview)
    return interview

@router.delete("/{interview_id}", status_code=status.HTTP_200_OK)
async def delete_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a scheduled interview. Admin only."""
    interview = db.query(Interview).filter(Interview.id == interview_id).first()

    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete interviews."
        )

    db.delete(interview)
    db.commit()

    return {"message": "Interview deleted successfully"}