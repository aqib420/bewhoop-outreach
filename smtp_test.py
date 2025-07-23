import smtplib
import ssl
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM")
SMTP_TO = os.getenv("SMTP_TO")

def send_test_email():
    message = f"""\
From: {SMTP_FROM}
To: {SMTP_TO}
Subject: SMTP Test Email

 This is a test email sent via Python using SMTP credentials from your .env file."""

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, SMTP_TO, message)
            print(" Email sent successfully!")
    except Exception as e:
        print(" Failed to send email:", str(e))

if __name__ == "__main__":
    send_test_email()
