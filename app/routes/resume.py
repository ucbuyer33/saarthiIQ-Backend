from pathlib import Path
import aiofiles # Async file handling ke liye (pip install aiofiles)
import uuid
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.resume import Resume
from app.models.candidate import Candidate
from app.models.user import User
from app.schemas.resume import ResumeResponse
from app.core.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)

UPLOAD_FOLDER = Path("uploads/resumes")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


# ==========================================
# 📤 Upload Resume (Async & Collision-Proof)
# ==========================================
@router.post("/upload/{candidate_id}", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_candidate_resume(
    candidate_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    # Security Guard: Only the creator of the candidate profile or admin can upload
    if candidate.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to alter this candidate profile.")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed.")

    # 1. Collision Prevention: Generate a unique filename using UUID
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = UPLOAD_FOLDER / unique_filename

    # 2. Asynchronous File Writing (Non-blocking I/O)
    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            while content := await file.read(1024 * 1024):  # Read in 1MB chunks
                await out_file.write(content)
    except Exception as e:
        logger.error(f"File system write failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to write file to storage.")

    # 3. Updated Model Fields Sync
    new_resume = Resume(
        file_name=file.filename,
        file_path=str(file_path),
        file_url=f"/static/resumes/{unique_filename}",  # Versatile storage independent path
        candidate_id=candidate_id
    )

    db.add(new_resume)
    
    # Optional Sync: Candidate table ka resume link ya status update kar do
    candidate.resume_url = new_resume.file_url

    db.commit()
    db.refresh(new_resume)
    return new_resume


# ==========================================
# 📊 Get All Resumes (Scope Protected)
# ==========================================
@router.get("/", response_model=List[ResumeResponse])
async def get_all_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Data Isolation: Normal recruiters see their own uploads; Admins see everything
    if hasattr(current_user, 'role') and current_user.role == "admin":
        return db.query(Resume).all()
        
    return db.query(Resume).join(Candidate).filter(Candidate.created_by == current_user.id).all()


# ==========================================
# 📥 Download Resume (Secure Access)
# ==========================================
@router.get("/download/{resume_id}")
async def download_candidate_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume record not found.")

    # Security Guard: Access control
    if resume.candidate.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to this document is restricted.")

    path = Path(resume.file_path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Physical file missing from server disk.")

    return FileResponse(
        path=str(path),
        filename=resume.file_name,
        media_type="application/pdf"
    )

# ==========================================
# 📄 Get Resumes By Candidate
# ==========================================
@router.get("/{candidate_id}", response_model=List[ResumeResponse])
async def get_resumes_by_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    if candidate.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view resumes for this candidate."
        )

    resumes = (
        db.query(Resume)
        .filter(Resume.candidate_id == candidate_id)
        .order_by(Resume.id.desc())
        .all()
    )

    return resumes

# ==========================================
# 🗑️ Delete Resume (Transaction Safe)
# ==========================================
@router.delete("/{resume_id}")
async def delete_candidate_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")

    # Security Guard
    if resume.candidate.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized request.")

    file_path = Path(resume.file_path)

    # 4. Safe Transaction: DB me se pehle udao, confirm hone ke baad disk clean karo
    candidate = resume.candidate
    if candidate and candidate.resume_url == resume.file_url:
        candidate.resume_url = None # Remove link from candidate reference

    db.delete(resume)
    db.commit()  # DB Transaction fully safe here!

    # Ab physical disk clear karo risk-free
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        logger.error(f"Failed to delete ghost file {file_path} from disk: {str(e)}")
        # Database commit safe ho chuka hai, user ko bad experience nahi milega

    return {"message": "Resume record and physical file deleted successfully."}