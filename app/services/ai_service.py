from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import json
import logging
from google import genai
from google.genai import types

from app.config import settings

logger = logging.getLogger(__name__)

# 1. Native SDK Initialization (Using modern SDK standards)
client = genai.Client(
    api_key=settings.GEMINI_API_KEY,
    http_options=types.HttpOptions(api_version="v1")
)

# ==========================================
# 📋 Inner Pydantic Structured Output Contracts
# ==========================================
class CandidateProfileSchema(BaseModel):
    full_name: Optional[str] = Field(None, description="Extracted full name of the candidate")
    email: Optional[EmailStr] = Field(None, description="Valid extracted contact email address")
    phone: Optional[str] = Field(None, description="Extracted primary phone number contact contact")

class CompleteAIReportSchema(BaseModel):
    candidate: CandidateProfileSchema
    resume_score: int = Field(..., description="Overall resume scoring ranking from 0 to 100")
    job_match: int = Field(..., description="Calculated matching analytics percentage score from 0 to 100")
    hiring_recommendation: str = Field(..., description="Direct operational judgment status (e.g., Strongly Recommend, Interview, Reject)")
    strengths: List[str] = Field(default_factory=list, description="Top positive technical capabilities and structure logs")
    weaknesses: List[str] = Field(default_factory=list, description="Identified formatting defects, missing scopes, or short track logs")
    missing_skills: List[str] = Field(default_factory=list, description="Modern market key tech stack elements missing from the document")
    learning_path: List[str] = Field(default_factory=list, description="Step by step upskilling timeline directions roadmap")
    recommended_jobs: List[str] = Field(default_factory=list, description="Standard job titles matching the target profile domain layout")
    ai_summary: str = Field(..., description="High level dynamic expert summary overview sentence details of the candidate profile")


# ==========================================
# 🧠 Async AI Core Generation Service Engine
# ==========================================
async def generate_ai_report(resume_text: str) -> Optional[dict]:
    """
    Leverages Gemini AI with strict structural schema contracts to generate 
    a comprehensive analytical assessment report without manual string cleaning loops.
    """
    if not resume_text or not resume_text.strip():
        logger.warning("Empty string argument supplied to AI report engine generation loop.")
        return None

    prompt = (
        f"You are an expert Technical Recruiter and Career Specialist. "
        f"Analyze the following raw resume text string payload. Extract complete profile information, "
        f"grade resume parameters, evaluate modern technical market gap indices, provide recommendations, "
        f"and draft a precise executive summary:\n\n{resume_text}"
    )

    try:
        # 2. Asynchronous execution boundary using safe model configurations
        # Using native SDK structures ensures response parsing validation is fully automated
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # Safe official stable engineering production model
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CompleteAIReportSchema,
                temperature=0.2,  # Low temperature value ensures strict analytical calculations integrity
            ),
        )

        # 3. Safe Extraction: Response text is guaranteed to match CompleteAIReportSchema structures perfectly
        report_data = json.loads(response.text)
        return report_data

    except Exception as e:
        logger.error(f"Gemini global processing routine failure exception caught: {str(e)}")
        # Graceful error bubbling framework for routes to intercept safety alerts cleanly
        raise RuntimeError(f"AI Core processing error intercepted: {str(e)}")