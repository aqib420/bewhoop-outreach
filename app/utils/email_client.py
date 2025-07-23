import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

async def send_email(to_email: str, subject: str, body: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()                
        server.starttls()
        server.ehlo()                
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
