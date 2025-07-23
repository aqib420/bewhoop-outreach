import asyncio
from aiosmtplib import SMTP
from email.message import EmailMessage

# SMTP config
SMTP_HOST = "mail.bewhoop.com"
SMTP_PORT = 587  # Use 587 for STARTTLS
SMTP_USER = "outreach@bewhoop.com"
SMTP_PASS = "your_password_here"  # replace this with the actual password

# Email content
FROM_EMAIL = SMTP_USER
TO_EMAIL = "muzamilhaider444@gmail.com"
SUBJECT = "SMTP Test"
BODY = "This is a test email from the BeWhoop outreach bot."

async def send_test_email():
    message = EmailMessage()
    message["From"] = FROM_EMAIL
    message["To"] = TO_EMAIL
    message["Subject"] = SUBJECT
    message.set_content(BODY)

    try:
        smtp = SMTP(hostname=SMTP_HOST, port=SMTP_PORT, use_tls=False)
        await smtp.connect()
        await smtp.starttls()
        await smtp.login(SMTP_USER, SMTP_PASS)
        await smtp.send_message(message)
        await smtp.quit()
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    asyncio.run(send_test_email())
