from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict, Any
import logging

from app.models.candidate import Candidate
from app.models.resume import Resume
from app.models.user import User

logger = logging.getLogger(__name__)

def get_dashboard_data(db: Session, current_user: User) -> Dict[str, Any]:
    """
    Computes secure candidate pipeline metadata metrics and tracks dynamic AI scoring 
    telemetry analytics tailored to user role access permissions.
    """
    is_admin = hasattr(current_user, 'role') and current_user.role == "admin"

    # 1. Tenancy Query Framing
    candidate_query = db.query(Candidate)
    resume_query = db.query(Resume)

    if not is_admin:
        candidate_query = candidate_query.filter(Candidate.created_by == current_user.id)
        resume_query = resume_query.join(Candidate).filter(Candidate.created_by == current_user.id)

    total_candidates = candidate_query.count()
    total_resumes = resume_query.count()

    # 2. Dynamic AI Scoring Computations (Populating placeholders safely)
    # Merging metrics calculations via built-in database filters
    score_stats = (
        db.query(
            func.avg(Resume.resume_score).label("avg_score"),
            func.count(Resume.id).filter(Resume.hiring_recommendation == "Strongly Recommend").label("highly_rec"),
            func.count(Resume.id).filter(Resume.hiring_recommendation == "Interview").label("rec"),
            func.count(Resume.id).filter(Resume.hiring_recommendation == "Consider").label("consider")
        )
        .join(Candidate)
        .filter(Candidate.created_by == current_user.id if not is_admin else True)
        .first()
    )

    # Clean float parse parameters
    average_score = round(float(score_stats.avg_score), 1) if score_stats and score_stats.avg_score else 0.0

    # 3. Dynamic Top Skills Processing Matrix (JSON Processing Helper)
    # Extracts items from candidate profiles skills arrays using database engine context
    skills_data = (
        db.query(Candidate.skills)
        .filter(Candidate.created_by == current_user.id if not is_admin else True)
        .all()
    )

    skills_frequencies = {}
    for entry in skills_data:
        # candidate.skills handles json lists directly as structured arrays
        if entry.skills and isinstance(entry.skills, list):
            for skill in entry.skills:
                normalized_skill = skill.strip().title()
                skills_frequencies[normalized_skill] = skills_frequencies.get(normalized_skill, 0) + 1

    # Sorting payload arrays to find the top 5 trending tech skills matches
    sorted_skills = sorted(skills_frequencies.items(), key=lambda item: item[1], reverse=True)[:5]
    top_skills_list = [skill_name for skill_name, count in sorted_skills]

    # 4. Recent Uploads Payload Aggregator
    # Returns the latest 5 resumes in database frame index context
    recent_resumes = (
        resume_query.order_by(desc(Resume.uploaded_at))
        .limit(5)
        .all()
    )

    recent_uploads_serialized = [
        {
            "id": res.id,
            "file_name": res.file_name,
            "candidate_name": res.candidate.full_name if res.candidate else "Unknown",
            "uploaded_at": res.uploaded_at
        }
        for res in recent_resumes
    ]

    # Final complete structured data map return
    return {
        "total_candidates": total_candidates,
        "total_resumes": total_resumes,
        "average_resume_score": average_score,
        "highly_recommended": score_stats.highly_rec if score_stats else 0,
        "recommended": score_stats.rec if score_stats else 0,
        "consider": score_stats.consider if score_stats else 0,
        "top_skills": top_skills_list,
        "recent_uploads": recent_uploads_serialized
    }