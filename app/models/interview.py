from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)

    # Candidate relationship with cascade deletion safety
    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # 1. Standard Improvement: Interviewer simple string se system User ID banaya
    interviewer_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True,
        index=True
    )
    
    # 2. Backup if interviewer is external (not registered in app)
    interviewer_name = Column(String, nullable=False)

    # E.g., "Technical Round 1", "HR Round", "System Design"
    interview_type = Column(String, nullable=False, index=True)
    
    # Timezone awareness sabse critical hai calendar scheduling ke liye
    interview_date = Column(DateTime(timezone=True), nullable=False)
    
    # Statuses: "Scheduled", "Rescheduled", "Completed", "Cancelled", "No Show"
    status = Column(String, default="Scheduled", index=True)
    
    # Feedback lamba ho sakta hai isliye Text use karna safe hai
    feedback = Column(Text, nullable=True)
    
    # 3. Calendar Meet Link mapping (Google Meet / Zoom integrations ke liye)
    meeting_link = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), 
        onupdate=func.now()
    )

    # Relationships mapping
    candidate = relationship("Candidate", back_populates="interviews")
    interviewer = relationship("User", back_populates="interviews")