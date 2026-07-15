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
    prefix="/resume-score",
    tags=["AI Resume Score"]
)

# 1. Pydantic Model strictly matching your requirements for structured output
class ResumeScoreSchema(BaseModel):
    resume_score: int = Field(..., description="Overall score out of 100 based on layout, depth, and impact.")
    strengths: List[str] = Field(default_factory=list, description="Top positive highlights of the candidate profile.")
    weaknesses: List[str] = Field(default_factory=list, description="Gaps, bad formatting areas, or missing tech details.")
    suggestions: List[str] = Field(default_factory=list, description="Actionable improvements to optimize the resume.")


# 2. Concurrency optimize karne ke liye async def use kiya
@router.post("/{resume_id}", response_model=ResumeScoreSchema)
async def evaluate_resume_score(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Evaluates candidate resume to extract performance score, key strengths, weaknesses, and optimization ideas.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume record not found."
        )

    # 3. Cache Match Optimization: PDF extraction se bacho agar textual database record active hai
    if resume.parsed_text:
        logger.info(f"Loading cached plain text for resume ID: {resume_id}")
        resume_text = resume.parsed_text
    else:
        logger.info(f"Extracting raw characters from file path for resume ID: {resume_id}")
        resume_text = extract_text_from_pdf(resume.file_path)
        
        if not resume_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unable to read text characters from candidate PDF."
            )
        
        # Save parsed plain text to cache layer
        resume.parsed_text = resume_text
        db.commit()

    # 4. Prompt Engineering Setup
    prompt = f"Analyze the following candidate resume text. Grade the profile score out of 100, identify strengths, list gaps or weaknesses, and share tips to improve it:\n\n{resume_text}"

    try:
        # 5. Native JSON Enforcement (No string parsing/splitting needed!)
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # Correct standard production engine
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ResumeScoreSchema,
                temperature=0.3, # Low temperature for analytical consistency
            ),
        )

        # Gemini output will perfectly validate against the response_model layout
        scorecard_json = json.loads(response.text)
        return scorecard_json

    except Exception as e:
        logger.error(f"Gemini resume scoring routine failed for ID {resume_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI engine failed to compute candidate score vectors. Please try again."
        )