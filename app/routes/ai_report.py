from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models.resume import Resume
from app.models.user import User
from app.core.dependencies import get_current_user
from app.core.pdf_reader import extract_text_from_pdf
from app.services.ai_service import generate_ai_report

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ai-report",
    tags=["AI Candidate Report"]
)

# 1. async def use kiya taaki I/O bound requests block na karein
@router.post("/{resume_id}", status_code=status.HTTP_200_OK)
async def create_ai_candidate_report(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch resume with candidate relation for saving audit/results later
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    # 2. Performance Cache Optimization:
    # Agar text pehle se parsed hai, toh wahi uthao. Baar-baar PDF parse mat karo.
    if resume.parsed_text:
        logger.info(f"Using cached text for resume ID: {resume_id}")
        resume_text = resume.parsed_text
    else:
        logger.info(f"Extracting text from PDF for resume ID: {resume_id}")
        resume_text = extract_text_from_pdf(resume.file_path)
        
        if not resume_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unable to extract text from the provided resume PDF."
            )
        
        # Save extracted text to cache for future requests
        resume.parsed_text = resume_text
        db.commit()

    try:
        # 3. Generate AI Report (Ensure your service handles the client call cleanly)
        report = generate_ai_report(resume_text)
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI service failed to generate report."
            )

        # 4. Optional Persistence Point: 
        # Agar tere candidate profile mein report field hai, toh yahan save kar do:
        # resume.candidate.ai_evaluation = report 
        # db.commit()

        return {"resume_id": resume_id, "report": report}

    except Exception as e:
        logger.error(f"Error generating AI report for resume {resume_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the AI report."
        )