import json
import logging
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Optional
from app.config import settings

# Setup Logger
logger = logging.getLogger(__name__)

# ==========================================
# 📋 Strict Pydantic Output Validation Schema
# ==========================================
class CandidateSubSchema(BaseModel):
    full_name: Optional[str] = Field(None, description="Full name of the candidate")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Contact number")

class ResumeSchema(BaseModel):
    candidate: CandidateSubSchema = Field(..., description="Personal identification records mapping")
    strengths: List[str] = Field(default_factory=list, description="List of core technical skills and expertise extracted")
    resume_score: int = Field(0, description="Overall ATS score based on quality between 0 to 100")
    hiring_recommendation: str = Field("Consider", description="Triage status: Strongly Recommend, Interview, Consider, or Reject")
    ai_summary: str = Field(..., description="Short executive text summary of the profile experience")
    missing_skills: List[str] = Field(default_factory=list, description="Key standard modern industry skills missing from text")
    learning_path: List[str] = Field(default_factory=list, description="Actionable upskilling roadmap bullet points")

# Create Google GenAI Client Instance
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# ==========================================
# 🧠 Asynchronous Gemini Report Generation Engine
# ==========================================
# 1. Function name synced to generate_ai_report & marked 'async' to protect event loop!
async def generate_ai_report(resume_text: str) -> Optional[dict]:
    """
    Parses resume text asynchronously using Gemini Structured Outputs.
    Returns a validated dictionary matching the router requirements or None if parsing fails.
    """
    if not resume_text.strip():
        logger.warning("Empty resume text provided to AI generation core.")
        return None

    prompt = (
        "Extract all professional details and perform an absolute structural analysis on this resume text. "
        "Calculate realistic score, strengths, critical missing tools gaps, and clear learning roadmaps:\n\n"
        f"{resume_text}"
    )

    try:
        logger.info("Initiating structural content generation call with gemini-2.5-flash...")
        
        # 2. Native Structured Output extraction loop execution
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ResumeSchema,  # Strict structure enforcement matching router payload
                temperature=0.1,               # Deterministic extraction extraction criteria
            ),
        )

        # 3. Direct response dictionary parsing without markdown code fence wrappers hacks
        parsed_data = json.loads(response.text)
        return parsed_data

    except json.JSONDecodeError as je:
        logger.error(f"Failed to decode structured JSON payload from Gemini response: {je}")
        return None
    except Exception as e:
        logger.error(f"Error while parsing resume with Gemini API framework layer: {str(e)}")
        return None