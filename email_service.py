"""SMTP email helper for sending password reset codes via Outlook."""
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

SMTP_HOST = "smtp-mail.outlook.com"
SMTP_PORT = 587


def _get_credentials():
    sender = os.environ.get("OUTLOOK_EMAIL")
    password = os.environ.get("OUTLOOK_PASSWORD")
    if not sender or not password:
        raise RuntimeError(
            "OUTLOOK_EMAIL and OUTLOOK_PASSWORD environment variables must be set."
        )
    return sender, password


def send_reset_code_email(recipient_email: str, recipient_name: str, code: str) -> bool:
    """Send a password reset code to the given email address.

    Returns True on success, False on failure (errors are logged).
    """
    try:
        sender, password = _get_credentials()
    except RuntimeError as e:
        logger.error(str(e))
        return False

    subject = "Your HCLV CareerNet password reset code"

    text_body = (
        f"Hello {recipient_name or 'there'},\n\n"
        f"You requested to reset your HCLV CareerNet password.\n\n"
        f"Your verification code is: {code}\n\n"
        f"This code expires in 15 minutes. If you did not request a reset, "
        f"please ignore this message.\n\n"
        f"— HCLV CareerNet"
    )

    html_body = f"""\
<!DOCTYPE html>
<html>
  <body style="font-family: Segoe UI, Arial, sans-serif; background:#f3f5f9; padding:24px; color:#1f2937;">
    <table align="center" cellpadding="0" cellspacing="0" width="100%" style="max-width:520px; background:#ffffff; border-radius:12px; box-shadow:0 6px 20px rgba(0,33,71,0.08); overflow:hidden;">
      <tr>
        <td style="background:linear-gradient(135deg,#002147,#003366); padding:24px; text-align:center; color:#ffffff;">
          <h1 style="margin:0; font-size:20px; letter-spacing:0.5px;">HCLV CareerNet</h1>
          <p style="margin:6px 0 0; font-size:13px; opacity:0.85;">Password reset request</p>
        </td>
      </tr>
      <tr>
        <td style="padding:28px;">
          <p style="margin:0 0 14px; font-size:15px;">Hello {recipient_name or 'there'},</p>
          <p style="margin:0 0 18px; font-size:14px; line-height:1.5;">
            We received a request to reset the password on your HCLV CareerNet account.
            Use the verification code below to continue:
          </p>
          <div style="text-align:center; margin:24px 0;">
            <div style="display:inline-block; background:#f1f3f5; border:1px solid #e2e8f0; border-radius:10px; padding:16px 28px; font-size:30px; font-weight:700; letter-spacing:8px; color:#002147; font-family:Consolas,Monaco,monospace;">
              {code}
            </div>
          </div>
          <p style="margin:0 0 12px; font-size:13px; color:#64748b;">
            This code expires in <strong>15 minutes</strong>.
          </p>
          <p style="margin:0; font-size:13px; color:#64748b;">
            If you did not request a password reset, you can safely ignore this email — your password will remain unchanged.
          </p>
        </td>
      </tr>
      <tr>
        <td style="background:#f8fafc; padding:14px 24px; text-align:center; color:#94a3b8; font-size:12px;">
          © HCLV CareerNet · Education for Service
        </td>
      </tr>
    </table>
  </body>
</html>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient_email
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender, password)
            server.sendmail(sender, [recipient_email], msg.as_string())
        logger.info(f"Sent password reset code to {recipient_email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Outlook SMTP auth failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to send reset email to {recipient_email}: {e}", exc_info=True)
        return False
