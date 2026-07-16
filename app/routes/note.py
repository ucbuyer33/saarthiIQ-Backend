from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db
from app.models.note import Note
from app.models.candidate import Candidate
from app.models.user import User
from app.schemas.note import NoteCreate, NoteUpdate # Assume NoteUpdate banaoge schemas me
from app.core.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/notes",
    tags=["Recruiter Notes"]
)


# ==========================================
# 📝 Add Note to Candidate
# ==========================================
@router.post("/{candidate_id}", status_code=status.HTTP_201_CREATED)
async def add_note(
    candidate_id: int,
    data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Adds an evaluation or internal note to a specific candidate profile safely."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Security Context: Owner validation guard (Admins bypass)
    if candidate.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to add remarks to this candidate profile."
        )

    new_note = Note(
        candidate_id=candidate_id,
        created_by=current_user.id,
        note=data.note
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


# ==========================================
# 🛠️ Update Note / Remarks
# ==========================================
@router.put("/{note_id}")
async def update_note(
    note_id: int,
    data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Allows the author or admin to update an existing note."""
    note_entry = db.query(Note).filter(Note.id == note_id).first()

    if not note_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    # Ownership Check: Only the creator of the note or an admin can edit it
    if note_entry.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only edit notes created by yourself."
        )

    note_entry.note = data.note
    # Database handles 'updated_at' auto-generation now
    
    db.commit()
    db.refresh(note_entry)
    return note_entry


# ==========================================
# 🗑️ Delete Note
# ==========================================
@router.delete("/{note_id}")
async def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletes an internal note reference safely."""
    note_entry = db.query(Note).filter(Note.id == note_id).first()

    if not note_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note reference not found"
        )

    # Authorization Check
    if note_entry.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to remove this note."
        )

    db.delete(note_entry)
    db.commit()
    return {"message": "Internal note deleted successfully"}