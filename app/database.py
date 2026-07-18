from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError  # 💡 Added for specific exception filtering
from typing import Generator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Cleanly hooks directly into our updated computed config model.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,          # Production scaling connection pool boundaries
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
    Ensures absolute execution termination bounds, error isolation, and connection cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        # 🛡️ Fix: Only log errors that are genuinely caused by database infrastructure or queries
        logger.error(f"Database infrastructure exception caught: {str(e)}")
        db.rollback()  # Best practice: Roll back failed database transactions explicitly
        raise
    except Exception:
        # 🚀 Let standard validation errors, 401s, 403s, and HTTPExceptions pass through silently
        raise
    finally:
        # Strict Execution Cleanup Contract
        db.close()