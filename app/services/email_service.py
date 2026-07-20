import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from app.config import settings

logger = logging.getLogger(__name__)


# ==========================================
# 📧 Brevo SMTP Email Engine
# ==========================================
def send_email(to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
    """
    Sends email via Brevo SMTP (smtp-relay.brevo.com:587).
    Free tier: 300 emails/day. No domain required. Works on all cloud hosts.
    """
    import smtplib
    try:
        message = MIMEMultipart("alternative" if is_html else "mixed")
        message["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
        message["To"] = to_email
        message["Subject"] = subject
        mime_type = "html" if is_html else "plain"
        message.attach(MIMEText(body, mime_type, "utf-8"))

        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            server.starttls()
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.sendmail(settings.MAIL_FROM, [to_email], message.as_string())

        logger.info(f"Email successfully dispatched to: {to_email}")
        return True

    except Exception as e:
        logger.error(f"Brevo SMTP transmission failure for {to_email}: {str(e)}")
        return False


# ==========================================
# 🎉 Welcome Email — Sent on Registration
# ==========================================
def send_welcome_email(to_email: str, full_name: str, user_id: str, role: str) -> bool:
    """
    Sends a branded HTML welcome email after successful user registration.
    Non-fatal — failure is logged as warning only.
    """
    role_color = "#6366f1" if role == "user" else "#0ea5e9"
    role_badge = "Recruitee" if role == "user" else "Recruiter"
    subject = f"Welcome to SaarthiIQ, {full_name.split()[0]}! 🎉"

    body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /></head>
    <body style="margin:0;padding:0;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:40px 0;">
        <tr><td align="center">
          <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

            <!-- HEADER -->
            <tr><td style="background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 100%);border-radius:12px 12px 0 0;padding:36px 40px;text-align:center;">
              <span style="color:white;font-size:24px;font-weight:700;">SaarthiIQ</span>
              <p style="color:rgba(255,255,255,0.75);font-size:12px;letter-spacing:2px;margin:8px 0 0;">AI RECRUITMENT PLATFORM</p>
            </td></tr>

            <!-- BODY -->
            <tr><td style="background:#ffffff;padding:40px;border-left:1px solid #e2e8f0;border-right:1px solid #e2e8f0;">
              <h1 style="margin:0 0 8px;font-size:26px;color:#1e293b;">Welcome aboard, {full_name.split()[0]}! 🚀</h1>
              <p style="margin:0 0 28px;color:#64748b;font-size:15px;">Your SaarthiIQ account is ready:</p>

              <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;margin-bottom:28px;">
                <tr><td style="padding:20px 24px;">
                  <table width="100%">
                    <tr><td style="padding:8px 0;border-bottom:1px solid #e2e8f0;">
                      <span style="color:#94a3b8;font-size:12px;font-weight:600;text-transform:uppercase;">Full Name</span><br/>
                      <span style="color:#1e293b;font-size:15px;">{full_name}</span>
                    </td></tr>
                    <tr><td style="padding:8px 0;border-bottom:1px solid #e2e8f0;">
                      <span style="color:#94a3b8;font-size:12px;font-weight:600;text-transform:uppercase;">Email</span><br/>
                      <span style="color:#1e293b;font-size:15px;">{to_email}</span>
                    </td></tr>
                    <tr><td style="padding:8px 0;border-bottom:1px solid #e2e8f0;">
                      <span style="color:#94a3b8;font-size:12px;font-weight:600;text-transform:uppercase;">User ID</span><br/>
                      <span style="color:#4f46e5;font-size:15px;font-weight:700;font-family:monospace;">{user_id}</span>
                    </td></tr>
                    <tr><td style="padding:8px 0;">
                      <span style="color:#94a3b8;font-size:12px;font-weight:600;text-transform:uppercase;">Account Type</span><br/>
                      <span style="display:inline-block;margin-top:4px;background:{role_color};color:white;font-size:12px;font-weight:600;padding:3px 10px;border-radius:20px;">{role_badge}</span>
                    </td></tr>
                  </table>
                </td></tr>
              </table>

              <p style="font-size:14px;color:#475569;margin:0 0 12px;font-weight:600;">What you can do now:</p>
              <table width="100%" style="margin-bottom:32px;">
                <tr><td style="padding:5px 0;"><span style="color:#4f46e5;margin-right:8px;">✦</span><span style="color:#475569;font-size:14px;">{'Browse job matches and upload your resume' if role == 'user' else 'Post campaigns and manage candidates'}</span></td></tr>
                <tr><td style="padding:5px 0;"><span style="color:#4f46e5;margin-right:8px;">✦</span><span style="color:#475569;font-size:14px;">{'Get AI-powered skill gap analysis' if role == 'user' else 'Schedule interviews and track progress'}</span></td></tr>
                <tr><td style="padding:5px 0;"><span style="color:#4f46e5;margin-right:8px;">✦</span><span style="color:#475569;font-size:14px;">View your personalised dashboard</span></td></tr>
              </table>

              <table width="100%"><tr><td align="center">
                <a href="https://saarthiiq-frontend.vercel.app/login"
                   style="display:inline-block;background:linear-gradient(135deg,#4f46e5,#7c3aed);color:white;font-size:15px;font-weight:600;padding:14px 36px;border-radius:8px;text-decoration:none;">
                  Go to Dashboard →
                </a>
              </td></tr></table>
            </td></tr>

            <!-- FOOTER -->
            <tr><td style="background:#f8fafc;border:1px solid #e2e8f0;border-top:none;border-radius:0 0 12px 12px;padding:24px 40px;text-align:center;">
              <p style="margin:0 0 4px;color:#94a3b8;font-size:12px;">Sent by <strong>SaarthiIQ Recruitment Operations Team</strong></p>
              <p style="margin:0;color:#cbd5e1;font-size:11px;">If you didn't create this account, ignore this email.</p>
            </td></tr>

          </table>
        </td></tr>
      </table>
    </body>
    </html>
    """
    return send_email(to_email, subject, body, is_html=True)
