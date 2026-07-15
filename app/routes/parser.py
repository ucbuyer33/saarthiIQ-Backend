from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.core.gemini_service import generate_ai_report
from app.models.resume import Resume
from app.models.candidate import Candidate
from app.models.user import User
# Assuming your auth extraction layer provides this dependency wrapper
# from app.core.dependencies import get_current_user 

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/parser", tags=["AI Resume Parser"])

@router.post("/analyze", status_code=status.HTTP_200_OK)
async def analyze_candidate_resume(
    resume_text: str, 
    candidate_id: int,
    db: Session = Depends(get_db)
    # current_user: User = Depends(get_current_user)
):
    """
    Triggers Gemini 2.5 Flash execution mapping over candidate records to 
    extract, score, and persist structured profile metadata in database.
    """
    # 1. Verification Guard
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Target Candidate profile registry not found")

    try:
        logger.info(f"Dispatching text payload to Gemini engine for Candidate ID: {candidate_id}")
        
        # 2. Fire Async AI Pipeline
        ai_payload = await generate_ai_report(resume_text)
        if not ai_payload:
            raise HTTPException(status_code=500, detail="AI Service returned empty serialization array")

        # 3. Synchronize Candidate Metadata directly from AI insights
        candidate_data = ai_payload.get("candidate", {})
        if candidate_data.get("full_name"):
            candidate.full_name = candidate_data["full_name"]
        
        # Store skill vectors in JSON table properties
        candidate.skills = ai_payload.get("strengths", [])
        candidate.status = "Applied"

        # 4. Save/Update Resume Analysis Matrix Linked Records
        resume = db.query(Resume).filter(Resume.candidate_id == candidate_id).first()
        if not resume:
            resume = Resume(candidate_id=candidate_id)
            db.add(resume)

        resume.resume_score = ai_payload.get("resume_score", 0)
        resume.hiring_recommendation = ai_payload.get("hiring_recommendation", "Consider")
        
        # Save parsed summary strings for dashboard quick reads
        resume.parsed_text = ai_payload.get("ai_summary", "") 
        # file_url proxy routing configurations handle context hooks dynamically
        resume.file_url = f"/api/resumes/download/{resume.id}" 

        db.commit()
        db.refresh(resume)
        
        return {
            "success": True,
            "message": "AI Resume report processed and database state synchronized successfully",
            "report": ai_payload
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Failed inside parser routing boundary execution thread: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI Engine Routing Crash: {str(e)}")