# saarthiIQ-Backend\app\models\user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    
    # Meaningful naming for clarity
    hashed_password = Column(String, nullable=False)
    
    # Roles: "admin", "recruiter", "interviewer", "user"
    role = Column(String, default="user", index=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ==========================================
    # 🎯 ORM Relationships (Connecting the dots)
    # ==========================================
    # Yeh saare models ko aapas me interconnect karega bina structural breakdown ke
    candidates = relationship("Candidate", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="creator")
    interviews = relationship("Interview", back_populates="interviewer")
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("Audit", back_populates="user")
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    timezone = Column(String, nullable=True)
    language = Column(String, nullable=True)
    theme = Column(String, nullable=True)
    notification_settings = Column(String, nullable=True)
    email_preferences = Column(String, nullable=True)
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")