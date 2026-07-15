from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# 1. Eliminated manual string reconstruction loop.
# Cleanly hooks directly into our updated computed config model.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,          # Added production scaling connection pool boundaries
    max_overflow=10,       # Allows extra temporary traffic burst handles slots
    pool_recycle=1800      # Prevents DB server side connection drops crashes
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# ==========================================
# 🔌 Database Session Injector Dependency
# ==========================================
def get_db() -> Generator:
    """
    FastAPI Context-aware generator dependency yielding safe database transactions.
    Ensures absolute execution termination bounds and connection recycling cleanup frames.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session lifecycle level exception caught: {str(e)}")
        raise
    finally:
        # 2. Strict Execution Cleanup Contract
        db.close()