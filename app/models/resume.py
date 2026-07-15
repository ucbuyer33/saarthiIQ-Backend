from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)

    # File details
    file_name = Column(String, nullable=False)
    
    # Path inside local storage or Cloud Bucket path
    file_path = Column(String, nullable=False)
    
    # Publicly accessible secure link (Supabase/S3 Storage URL)
    file_url = Column(String, nullable=True)

    # 1. Performance Optimizer: Plain text extracted from PDF
    # Isko save karne se keyword search (`routes/search.py`) instant ho jata hai
    parsed_text = Column(Text, nullable=True)

    # 2. Strong Cascading Relationship
    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Double-sided ORM relationship linking
    candidate = relationship("Candidate", back_populates="resumes")