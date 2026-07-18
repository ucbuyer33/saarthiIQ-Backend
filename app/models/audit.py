# saarthiIQ-Backend\app\models\audit.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base

class Audit(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # E.g., "CREATE", "UPDATE", "DELETE", "LOGIN_FAILED"
    action = Column(String, nullable=False, index=True)
    
    # E.g., "candidate", "resume", "auth", "interview"
    module = Column(String, nullable=False, index=True)
    
    # Foreign key with safe deletion handling
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True
    )
    
    # 1. Sabse Important: Purani aur nayi values ya extra details store karne ke liye
    # E.g., {"previous_status": "applied", "new_status": "shortlisted"}
    details = Column(JSON, nullable=True)
    
    # 2. Security Context Columns
    ip_address = Column(String(45), nullable=True)  # Supports both IPv4 and IPv6
    user_agent = Column(String, nullable=True)      # Browser/Device info
    
    # Automatic Timezone aware creation timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationship setup (Optional but helps in querying)
    user = relationship("User", back_populates="audit_logs")