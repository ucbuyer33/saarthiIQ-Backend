from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # ── Human-readable ID  (RC889234) ─────────────────────────────────────────
    # Generated once on registration via app.utils.id_gen.generate_user_id().
    # Stored as a plain indexed string; unique constraint prevents collisions.
    user_id = Column(String(8), unique=True, index=True, nullable=True)

    full_name = Column(String, nullable=False, index=True)
    email     = Column(String, unique=True, index=True, nullable=False)

    hashed_password = Column(String, nullable=False)

    # Single-role app: every account is a recruiter. No `role` column needed.
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ── Profile fields ────────────────────────────────────────────
    phone                 = Column(String, nullable=True)
    location              = Column(String, nullable=True)
    timezone              = Column(String, nullable=True)
    language              = Column(String, nullable=True)
    theme                 = Column(String, nullable=True)
    notification_settings = Column(String, nullable=True)
    email_preferences     = Column(String, nullable=True)

    # ── Relationships ──────────────────────────────────────────────
    candidates  = relationship("Candidate",    back_populates="user",        cascade="all, delete-orphan")
    tasks       = relationship("Task",         back_populates="user",        cascade="all, delete-orphan")
    campaigns   = relationship("Campaign",     back_populates="creator")
    interviews  = relationship("Interview",    back_populates="interviewer")
    notes       = relationship("Note",         back_populates="user",        cascade="all, delete-orphan")
    audit_logs  = relationship("Audit",        back_populates="user")
    sessions    = relationship("UserSession",  back_populates="user",        cascade="all, delete-orphan")
