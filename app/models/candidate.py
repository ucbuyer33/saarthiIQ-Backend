from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    
    # Core Details
    full_name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=False)
    
    # 1. Structured Data (JSON ya Array use karein advanced filtering ke liye)
    # E.g., ["Python", "Docker", "Machine Learning"]
    skills = Column(JSON, nullable=True, default=[])
    
    # Professional details
    experience = Column(String, nullable=True) # Text summary or years
    location = Column(String, nullable=True, index=True)
    resume_url = Column(String, nullable=True) # Supabase storage public link
    
    # Statuses: "Applied", "Shortlisted", "Interviewing", "Offered", "Rejected"
    status = Column(String, default="Applied", index=True)
    
    # Auditor & Ownership linking
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

    # 2. Strong Relationships Mapping
    user = relationship("User", back_populates="candidates")
    
    # 3. Future Extensions (Jo tune models list mein banaye the)
    resumes = relationship("Resume", back_populates="candidate", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="candidate", cascade="all, delete-orphan")
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)