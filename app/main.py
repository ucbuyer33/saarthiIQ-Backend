# saarthiIQ-Backend\app\main.py
# Add this temporarily
try:
    from create_admin import main as create_admin_user
    create_admin_user()
    print("--- ADMIN CREATION SCRIPT EXECUTED ---")
except Exception as e:
    print(f"--- ADMIN CREATION FAILED: {e} ---")
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import Base, engine

# Models Sync
from app.models.user import User
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.models.note import Note
from app.models.interview import Interview
from app.models.campaign import Campaign
from app.models.audit import Audit

# API Routers Core Injections
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.candidates import router as candidates_router
from app.routes.resume import router as resume_router
from app.routes.parser import router as parser_router
from app.routes.resume_score import router as resume_score_router
from app.routes.job_match import router as job_match_router  # Router imported cleanly!
from app.routes.skill_gap import router as skill_gap_router
from app.routes.ai_report import router as ai_report_router
from app.routes.dashboard import router as dashboard_router
from app.routes.search import router as search_router
from app.routes.note import router as notes_router
from app.routes.interviews import router as interview_router
from app.routes.campaigns import router as campaigns_router
from app.routes.tasks import router as tasks_router
from app.routes.audit import router as audit_router
from app.routes.analytics import router as analytics_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing system configurations database engine...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database structural framework synchronized successfully.")
    yield
    logger.info("Shutting down application server sockets pools...")

# Central global app context initiation
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(candidates_router)
app.include_router(resume_router)
app.include_router(parser_router)
app.include_router(resume_score_router)
app.include_router(job_match_router)  # Mounted cleanly here!
app.include_router(skill_gap_router)
app.include_router(ai_report_router)
app.include_router(dashboard_router)
app.include_router(search_router)
app.include_router(notes_router)
app.include_router(interview_router)
app.include_router(campaigns_router)
app.include_router(tasks_router)
app.include_router(audit_router)
app.include_router(analytics_router)

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {"status": "Running", "application": settings.PROJECT_NAME, "version": settings.PROJECT_VERSION}

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"message": "SaarthiIQ system state is fully optimized and functional", "timestamp": "Active"}
