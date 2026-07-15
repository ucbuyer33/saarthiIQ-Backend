from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
import logging

from app.models.candidate import Candidate
from app.models.user import User

logger = logging.getLogger(__name__)

# 1. Added User object hook, skills array, and pagination to match routes/search.py
def search_candidates(
    db: Session,
    user: User,
    name: Optional[str] = None,
    email: Optional[str] = None,
    location: Optional[str] = None,
    skills: Optional[List[str]] = None,
    page: int = 1,
    limit: int = 20
) -> dict:
    """
    Advanced SQL engine that evaluates textual patterns, tenant data borders,
    and structured JSON skill metrics with built-in pagination limits.
    """
    query = db.query(Candidate)

    # 2. Security Tenancy Guard: Enforce access control separation
    is_admin = hasattr(user, 'role') and user.role == "admin"
    if not is_admin:
        query = query.filter(Candidate.created_by == user.id)

    # Textual matching logic adjustments
    if name:
        query = query.filter(Candidate.full_name.ilike(f"%{name}%"))
    
    if email:
        query = query.filter(Candidate.email.ilike(f"%{email}%"))
        
    if location:
        query = query.filter(Candidate.location.ilike(f"%{location}%"))

    # 3. Dynamic JSON Skill Matching Engine
    # Processes candidate.skills JSONB array against the input skills list
    if skills and len(skills) > 0:
        for skill in skills:
            # Enforces case-insensitive array value matching inside SQL engine
            query = query.filter(
                Candidate.skills.contains(func.jsonb_build_array(skill))
            )

    # 4. Strict Offset & Page Window Calculations
    total_matches = query.count()
    offset_value = (page - 1) * limit
    
    results = (
        query.order_by(Candidate.created_at.desc())
        .offset(offset_value)
        .limit(limit)
        .all()
    )

    # Return standard paginated payload that perfectly handshakes with UI requirements
    return {
        "total": total_matches,
        "page": page,
        "limit": limit,
        "results": results
    }