from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from app.models.candidate import Candidate
from app.models.user import User
from app.models.interview import Interview
from app.models.task import Task
from app.models.campaign import Campaign

logger = logging.getLogger(__name__)

# 1. Added current_user context hook to enforce corporate tenant data isolation
def get_dashboard_stats(db: Session, current_user: User) -> dict:
    """
    Computes secure operational counters and dynamic stage pipeline metrics 
    isolated precisely based on user authentication scope authorization boundaries.
    """
    is_admin = hasattr(current_user, 'role') and current_user.role == "admin"
    
    # Base Dynamic Query initializations
    candidate_query = db.query(Candidate)
    task_query = db.query(Task)
    campaign_query = db.query(Campaign)
    interview_query = db.query(Interview)

    # 2. Security Tenancy Enforcement Rules Guard (Non-admins can only see their own domain updates)
    if not is_admin:
        candidate_query = candidate_query.filter(Candidate.created_by == current_user.id)
        task_query = task_query.filter(Task.assigned_to == current_user.id)
        campaign_query = campaign_query.filter(Campaign.created_by == current_user.id)
        # Assuming interviewer context is mapped via system identity link
        interview_query = interview_query.filter(Interview.interviewer_id == current_user.id)

    # Calculate Isolated Numerical Totals
    total_candidates = candidate_query.count()
    total_tasks = task_query.count()
    total_campaigns = campaign_query.count()
    total_interviews = interview_query.count()
    
    # Admins see complete platform members strength counter; recruiters see isolated index value 1 fallback
    total_users = db.query(User).count() if is_admin else 1

    # 3. Dynamic Pipeline Status Breakdown Engine Generation Loop
    # Grouping queries using SQL aggregates provides high computational execution speed
    status_counts = (
        db.query(Candidate.status, func.count(Candidate.id))
        .filter(Candidate.created_by == current_user.id if not is_admin else True)
        .group_by(Candidate.status)
        .all()
    )

    # Initialize complete target schema compliant structural keys dictionary 
    breakdown_matrix = {
        "Applied": 0,
        "Interviewing": 0,
        "Shortlisted": 0,
        "Rejected": 0
    }

    # Map dynamic query values safely over standard expected statuses keys
    for status_label, counter_value in status_counts:
        if status_label in breakdown_matrix:
            breakdown_matrix[status_label] = counter_value

    # 4. Perfectly Formatted Output Payload Map match for routes/dashboard.py response validation
    return {
        "total_candidates": total_candidates,
        "total_users": total_users,
        "total_interviews": total_interviews,
        "total_tasks": total_tasks,
        "total_campaigns": total_campaigns,
        "candidate_status_breakdown": breakdown_matrix
    }