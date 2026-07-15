from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)

    # Candidate tracking link
    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Note creater (HR / Interviewer) tracking link
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"), # Safe cascading if user is deleted
        nullable=False,
        index=True
    )

    # String ki jagah Text use kiya jo unbounded remarks ke liye accurate hai
    note = Column(Text, nullable=False)

    # Dynamic Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), 
        onupdate=func.now()
    )

    # Double-sided ORM relations mapping
    candidate = relationship("Candidate", back_populates="notes")
    user = relationship("User", back_populates="notes")