from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    
    campaign_name = Column(String, nullable=False, index=True)
    subject = Column(String, nullable=False)
    message = Column(String, nullable=False)  # Supports HTML or plain text templates
    
    # Statuses: "Draft", "Scheduled", "Processing", "Completed", "Failed"
    status = Column(String, default="Draft", index=True)
    
    # 1. Performance Counters (Analytics ke liye bohot zaroori)
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    open_count = Column(Integer, default=0)  # tracking pixel ke liye
    
    # 2. Scheduling Timestamps
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # User linkage with safe cascading
    created_by = Column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True
    )
    
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    updated_at = Column(
        DateTime(timezone=True), 
        onupdate=func.now()
    )

    # Relationships (FastAPI me data fetch karte waqt bohot kaam aayega)
    creator = relationship("User", back_populates="campaigns")
    
    # Kal ko agar 'candidates' ko campaign me add karegi, toh Many-to-Many logic yahan link hoga