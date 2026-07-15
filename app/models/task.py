from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    
    title = Column(String, nullable=False, index=True)
    
    # Description lamba ho sakta hai isliye Text use karna safe hai
    description = Column(Text, nullable=True)
    
    # Statuses: "Pending", "In Progress", "Completed", "Cancelled"
    status = Column(String, default="Pending", index=True)
    
    # Priorities: "Low", "Medium", "High", "Critical"
    priority = Column(String, default="Medium", index=True)
    
    # Timezone aware due date for accurate email/system reminders
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Task assignment with safe cascading if the user is deleted
    assigned_to = Column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True,
        index=True
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

    # Clean double-sided relationship mapping
    user = relationship("User", back_populates="tasks")