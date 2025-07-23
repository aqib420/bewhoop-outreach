# app/services/email_service.py

from aiosmtplib import SMTP
from email.message import EmailMessage
import os

SMTP_HOST = os.getenv("SMTP_HOST", "mail.bewhoop.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USERNAME")  # make sure your .env has SMTP_USERNAME
SMTP_PASS = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("SMTP_FROM", SMTP_USER)

async def send_email_to_vendor(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        smtp = SMTP(
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            use_tls=True  # Connect with SSL directly on port 465
        )
        await smtp.connect()
        await smtp.login(SMTP_USER, SMTP_PASS)
        await smtp.send_message(msg)
        await smtp.quit()
        return True
    except Exception as e:
        raise Exception(f"Failed to send email: {e}")
