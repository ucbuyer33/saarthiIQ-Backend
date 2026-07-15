from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database import get_db, SessionLocal
from app.models.campaign import Campaign
from app.models.user import User
from app.schemas.campaign import CampaignCreate, CampaignUpdate
from app.core.dependencies import get_current_user
from app.services.email_service import send_email
from app.models.candidate import Candidate

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/campaigns",
    tags=["Email Campaigns"]
)

# ==========================================
# 🚀 Background Task Function
# ==========================================
def process_campaign_emails_bg(campaign_id: int):
    """Runs in the background so the UI doesn't freeze."""
    db = SessionLocal() # New session for background task
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        candidates = db.query(Candidate).filter(Candidate.email.isnot(None)).all()

        campaign.total_recipients = len(candidates)
        campaign.status = "Processing"
        db.commit()

        sent = 0
        for candidate in candidates:
            success = send_email(
                to_email=candidate.email,
                subject=campaign.subject,
                message=campaign.message
            )
            if success:
                sent += 1
                
        # Update final stats
        campaign.sent_count = sent
        campaign.status = "Completed"
        db.commit()
        
    except Exception as e:
        logger.error(f"Campaign {campaign_id} failed: {str(e)}")
        if campaign:
            campaign.status = "Failed"
            db.commit()
    finally:
        db.close()


# ==========================================
# 🌐 API Routes
# ==========================================

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def create_campaign(
    data: CampaignCreate,
    background_tasks: BackgroundTasks, # FastAPI native background runner
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates a campaign and schedules emails in the background."""
    new_campaign = Campaign(
        campaign_name=data.campaign_name,
        subject=data.subject,
        message=data.message,
        created_by=current_user.id,
        status="Scheduled" # Initially scheduled
    )

    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)

    # Handover the heavy lifting to the background task
    background_tasks.add_task(process_campaign_emails_bg, new_campaign.id)

    return {
        "message": "Campaign created and emails are being processed in the background.",
        "campaign_id": new_campaign.id,
        "status": new_campaign.status
    }


@router.get("/", status_code=status.HTTP_200_OK)
async def get_campaigns(
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches paginated campaigns. Users see their own; Admins see all."""
    query = db.query(Campaign)
    
    # Ownership Check
    if hasattr(current_user, 'role') and current_user.role != "admin":
        query = query.filter(Campaign.created_by == current_user.id)
        
    offset = (page - 1) * limit
    campaigns = query.order_by(Campaign.created_at.desc()).offset(offset).limit(limit).all()
    
    return {"page": page, "limit": limit, "results": campaigns}


@router.put("/{campaign_id}")
async def update_campaign(
    campaign_id: int,
    data: CampaignUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Security: Ensure only the creator or admin can update
    if campaign.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to modify this campaign")

    # Don't update if it's already sent
    if campaign.status in ["Processing", "Completed"]:
        raise HTTPException(status_code=400, detail="Cannot modify a campaign that is already processed.")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(campaign, key, value)

    db.commit()
    db.refresh(campaign)
    return campaign


@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this campaign")

    db.delete(campaign)
    db.commit()
    return {"message": "Campaign deleted successfully"}