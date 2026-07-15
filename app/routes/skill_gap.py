from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List
import json
import logging
from google.genai import types

from app.database import get_db
from app.models.resume import Resume
from app.models.user import User
from app.core.dependencies import get_current_user
from app.core.pdf_reader import extract_text_from_pdf
from app.core.gemini_service import client

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/skill-gap",
    tags=["AI Skill Gap Analysis"]
)

# 1. Strict Pydantic Schema for seamless API response binding
class SkillGapAnalysisSchema(BaseModel):
    current_skills: List[str] = Field(default_factory=list, description="Skills present inside the resume.")
    missing_skills: List[str] = Field(default_factory=list, description="Crucial modern market gaps identified in their domain.")
    learning_path: List[str] = Field(default_factory=list, description="Step-by-step career path or milestones to fill gaps.")
    estimated_learning_time: str = Field(..., description="Estimated dynamic timeframe to upskill (e.g., '3-6 months').")


# 2. Turned to async def to unlock FastAPI concurrency
@router.post("/{resume_id}", response_model=SkillGapAnalysisSchema)
async def analyze_candidate_skill_gap(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Performs precise technical skill gap analytics and roadmap planning via Gemini AI.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume record not found."
        )

    # 3. Cache Optimization Check: PDF read skip layer
    if resume.parsed_text:
        logger.info(f"Loading plain text cache data for resume ID: {resume_id}")
        resume_text = resume.parsed_text
    else:
        logger.info(f"Parsing raw PDF file from storage for resume ID: {resume_id}")
        resume_text = extract_text_from_pdf(resume.file_path)
        
        if not resume_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unable to extract readable textual data characters from candidate document."
            )
        
        # Save plain text to DB cache immediately
        resume.parsed_text = resume_text
        db.commit()

    # 4. Prompt Engineering Context
    prompt = (
        f"You are an expert Career Coach and Technical Recruiter. "
        f"Analyze the following resume text. List current skills, discover technical gaps compared to standard modern industry expectations, "
        f"build a realistic step-by-step learning roadmap, and estimate upskilling time:\n\n{resume_text}"
    )

    try:
        # 5. Native Type Enforcement via SDK (Zero manual cleaning code needed!)
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # Safe standard core engine
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SkillGapAnalysisSchema,
                temperature=0.3, # Fair balance between analytics and structure
            ),
        )

        # Output is guaranteed to format safely under SkillGapAnalysisSchema data contract
        gap_report_json = json.loads(response.text)
        return gap_report_json

    except Exception as e:
        logger.error(f"Gemini skill gap matrix generation failed for resume {resume_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service failed to model skill gap parameters. Please try again."
        )