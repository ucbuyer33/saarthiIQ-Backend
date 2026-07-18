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
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Optional[Audit]:
    try:
        log = Audit(
            action=action,
            module=module,
            user_id=user_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(log)
        db.flush()
        return log
    except Exception as e:
        logger.error(f"Failed to stage audit log: {str(e)}")
        return None