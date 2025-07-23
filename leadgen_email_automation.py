import imaplib
import smtplib
import email
import os
from datetime import datetime
from email.message import EmailMessage
from config import EMAIL_USER, EMAIL_PASS, IMAP_SERVER, SMTP_SERVER, SMTP_PORT

def fetch_latest_email_from(sender_email):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select('"[Gmail]/Spam"')

    # Search for emails FROM the sender
    status, messages = mail.search(None, f'(FROM "{sender_email}")')
    email_ids = messages[0].split()
    
    if not email_ids:
        print("No emails found.")
        return None

    latest_email_id = email_ids[-1]
    status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
    raw_email = msg_data[0][1]

    msg = email.message_from_bytes(raw_email)
    subject = msg["Subject"]
    from_email = msg["From"]
    msg_id = msg["Message-ID"]

    print(f"Fetched Email from: {from_email}, Subject: {subject}")
    return from_email, subject, msg_id

def reply_to_email(to_email, subject, in_reply_to_msg_id):
    reply = EmailMessage()
    reply["Subject"] = "Re: " + subject
    reply["From"] = EMAIL_USER
    reply["To"] = to_email
    reply["In-Reply-To"] = in_reply_to_msg_id
    reply["References"] = in_reply_to_msg_id
    reply.set_content("Hi! 👋 This is an automated reply from our system. We'll get back to you shortly.")

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(reply)
        print(f"✅ Replied to: {to_email}")
    save_reply_log(to_email, reply["Subject"], reply.get_content())

def save_reply_log(to_email, subject, reply_body):
    os.makedirs("sent_logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"sent_logs/reply_{timestamp}.txt"
    print(f"📝 Saving log to: {filename}")  # Add this line
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"To: {to_email}\nSubject: {subject}\n\n{reply_body}")



if __name__ == "__main__":
    from_email = "outreach@bewhoop.com"  # Sender to look for
    result = fetch_latest_email_from(from_email)

    if result:
        from_email, subject, msg_id = result
        reply_to_email(from_email, subject, msg_id)
    else:
        print("❌ No matching emails to reply to.")



