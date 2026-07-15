import aiosmtplib  # Non-blocking async SMTP client support ke liye
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

# ==========================================
# 📧 Asynchronous & Secure Email Engine
# ==========================================
async def send_email(to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
    """
    Dispatches emails asynchronously via aiosmtplib to protect FastAPI's event loop.
    Supports continuous background task workers execution safely.
    """
    try:
        # 1. Message Construction
        message = MIMEMultipart("alternative" if is_html else "mixed")
        message["From"] = settings.MAIL_FROM
        message["To"] = to_email
        message["Subject"] = subject

        # Flexible format handler (Plain text vs Rich HTML Layouts)
        mime_type = "html" if is_html else "plain"
        message.attach(MIMEText(body, mime_type, "utf-8"))

        # 2. Asynchronous SMTP connection context mapping
        # This prevents blocking main thread loops during network I/O spikes
        async with aiosmtplib.SMTP(
            hostname=settings.MAIL_SERVER,
            port=settings.MAIL_PORT,
            use_tls=(settings.MAIL_PORT == 465)  # Auto switch based on standard port configurations
        ) as server:
            
            # StartTLS configuration check for non-pure SSL connections (Port 587 setup)
            if settings.MAIL_PORT != 465:
                await server.starttls()
                
            # Perform Async Login
            await server.login(
                settings.MAIL_USERNAME,
                settings.MAIL_PASSWORD
            )
            
            # Dynamic Dispatch execution
            await server.sendmail(
                settings.MAIL_FROM,
                [to_email],
                message.as_string()
            )
            
        logger.info(f"Email successfully dispatched to reference target: {to_email}")
        return True

    except Exception as e:
        # Production standard logging layer integration
        logger.error(f"Async email engine transmission failure for {to_email}: {str(e)}")
        return False