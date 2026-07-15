from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List, Optional
import math
import re
import logging

from app.database import get_db
from app.services.audit_service import log_action

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ml", tags=["Machine Learning Matcher"])

class MatchPayloadSchema(BaseModel):
    job_description: str = Field(..., min_length=10, description="Raw text context specifications of the opening target")
    candidate_skills: List[str] = Field(..., description="Extracted tech stack list array from candidate profile")
    candidate_id: Optional[int] = Field(None, description="Optional target reference identity links to enable database auditing log tracking")

def tokenize_and_clean(text: str) -> List[str]:
    return re.findall(r'\w+', text.lower())

def compute_binary_cosine_similarity(jd_text: str, skills_list: List[str]) -> float:
    jd_words = set(tokenize_and_clean(jd_text))
    skills_normalized = set()
    for skill in skills_list:
        for word in tokenize_and_clean(skill):
            skills_normalized.add(word)

    if not jd_words or not skills_normalized:
        return 0.0

    vocabulary = jd_words | skills_normalized
    v_jd = {word: (1 if word in jd_words else 0) for word in vocabulary}
    v_skills = {word: (1 if word in skills_normalized else 0) for word in vocabulary}

    dot_product = sum(v_jd[w] * v_skills[w] for w in vocabulary)
    magnitude_jd = math.sqrt(sum(v_jd[w] ** 2 for w in vocabulary))
    magnitude_skills = math.sqrt(sum(v_skills[w] ** 2 for w in vocabulary))

    denominator = magnitude_jd * magnitude_skills
    if not denominator:
        return 0.0
        
    return round(float(dot_product) / denominator, 4)

@router.post("/job-match-score", status_code=status.HTTP_200_OK)
async def calculate_semantic_job_match(payload: MatchPayloadSchema, db: Session = Depends(get_db)):
    try:
        if not payload.candidate_skills:
            return {"match_percentage": 0, "hiring_recommendation_tier": "Reject"}

        similarity_coefficient = compute_binary_cosine_similarity(payload.job_description, payload.candidate_skills)
        match_percentage = min(int(similarity_coefficient * 100 * 1.8), 100)

        if match_percentage >= 75:
            tier = "Strongly Recommend"
        elif match_percentage >= 50:
            tier = "Interview"
        elif match_percentage >= 30:
            tier = "Consider"
        else:
            tier = "Reject"

        if payload.candidate_id:
            log_action(
                db=db, action="MATCH_CALCULATION", module="ml_matcher", user_id=None,
                details={"candidate_id": payload.candidate_id, "computed_score": match_percentage, "tier_outcome": tier}
            )
            db.commit()

        return {
            "match_percentage": match_percentage,
            "matching_coefficient_score": round(similarity_coefficient, 2),
            "hiring_recommendation_tier": tier,
            "indexed_candidate_skills_count": len(payload.candidate_skills)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))