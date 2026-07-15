from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import logging

from app.models.audit import Audit

logger = logging.getLogger(__name__)

def log_action(
    db: Session,
    action: str,
    module: str,
    user_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None
) -> Audit:
    """
    Spawns an audit log entry inside the staging transaction pipeline.
    Avoids aggressive committing to ensure parent DB transactions maintain atomicity.
    """
    try:
        # 1. Advanced Structural Metadata Extraction
        log = Audit(
            action=action,
            module=module,
            user_id=user_id,
            details=details  # Captures JSON state transitions dynamically
        )

        db.add(log)
        
        # 2. Production Commit Rule (db.flush instead of db.commit):
        # We flush it to populate the ID and timestamp properties in memory 
        # but let the main API route handle the final atomic .commit(). 
        # If the main action crashes, the audit trail rolls back safely!
        db.flush()
        return log

    except Exception as e:
        # Compliance fail-safe log buffer (Don't let logging failures crash main pipeline flows)
        logger.error(f"Failed to stage system audit log entity tracking matrix: {str(e)}")
        # We swallow or pass depending on strict compliance protocols. In production, we pass.
        return None