# import imaplib
# import email
# from email.header import decode_header
# import os
# from dotenv import load_dotenv
# import datetime

# # Create folder if not exists
# LOG_DIR = "email_logs"
# os.makedirs(LOG_DIR, exist_ok=True)


# # Load .env variables
# load_dotenv()

# # Read IMAP credentials
# IMAP_HOST = os.getenv("IMAP_HOST")
# IMAP_USER = os.getenv("IMAP_USERNAME")
# IMAP_PASS = os.getenv("IMAP_PASSWORD")

# def clean(text):
#     return "".join(c if c.isalnum() else "_" for c in text)

# def fetch_replies():
#     imap = imaplib.IMAP4_SSL(IMAP_HOST)

#     try:
#         imap.login(IMAP_USER, IMAP_PASS)
#         print(f"✅ Logged in as {IMAP_USER}")
#     except imaplib.IMAP4.error as e:
#         print(f"❌ Login failed: {e}")
#         return

#     imap.select("INBOX")

#     # Get all emails (or use 'UNSEEN' to only fetch unread replies)
#     status, messages = imap.search(None, "ALL")
#     email_ids = messages[0].split()

#     print(f"📥 Total emails found: {len(email_ids)}")

#     for eid in email_ids[-10:]:  # Just the last 10 emails
#         res, msg_data = imap.fetch(eid, "(RFC822)")
#         if res != "OK":
#             print(f"⚠️ Failed to fetch email {eid.decode()}")
#             continue

#         raw_email = msg_data[0][1]
#         msg = email.message_from_bytes(raw_email)

#         # Decode subject
#         subject, encoding = decode_header(msg["Subject"])[0]
#         if isinstance(subject, bytes):
#             subject = subject.decode(encoding or "utf-8", errors="ignore")

#         from_ = msg.get("From")
#         print("\n" + "="*50)
#         print(f"📨 From: {from_}")
#         print(f"📝 Subject: {subject}")

#         body = ""
#         if msg.is_multipart():
#             for part in msg.walk():
#                 if part.get_content_type() == "text/plain":
#                     try:
#                         body = part.get_payload(decode=True).decode(errors="ignore")
#                         break
#                     except:
#                         continue
#         else:
#             try:
#                 body = msg.get_payload(decode=True).decode(errors="ignore")
#             except:
#                 body = "[Could not decode]"

#         print(f"📄 Body:\n{body[:300]}")
#         # Save to file
#         timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#         filename = f"reply_{timestamp}.txt"
#         filepath = os.path.join(LOG_DIR, filename)

#         with open(filepath, "w", encoding="utf-8") as f:
#             f.write(f"From: {from_}\n")
#             f.write(f"Subject: {subject}\n\n")
#             f.write(body)

#         print(f"💾 Saved reply to: {filepath}")

#     imap.logout()

# if __name__ == "__main__":
#     fetch_replies()
# app/email_ingestion/imap_fetch_replies.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv
import datetime
import asyncio

from app.db.database import get_db
from app.email_ingestion.email_utils import save_email_to_db

# Create folder if not exists
LOG_DIR = "email_logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Load .env variables
load_dotenv()

# Read IMAP credentials
IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_USER = os.getenv("IMAP_USERNAME")
IMAP_PASS = os.getenv("IMAP_PASSWORD")

def clean(text):
    return "".join(c if c.isalnum() else "_" for c in text)

async def fetch_and_store_replies():
    imap = imaplib.IMAP4_SSL(IMAP_HOST)

    try:
        imap.login(IMAP_USER, IMAP_PASS)
        print(f"✅ Logged in as {IMAP_USER}")
    except imaplib.IMAP4.error as e:
        print(f"❌ Login failed: {e}")
        return

    imap.select("INBOX")
    status, messages = imap.search(None, "ALL")
    email_ids = messages[0].split()

    print(f"📥 Total emails found: {len(email_ids)}")

    async for db in get_db():
        for eid in email_ids[-10:]:  # last 10 emails
            res, msg_data = imap.fetch(eid, "(RFC822)")
            if res != "OK":
                print(f"⚠️ Failed to fetch email {eid.decode()}")
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8", errors="ignore")

            from_ = msg.get("From")

            print("\n" + "="*50)
            print(f"📨 From: {from_}")
            print(f"📝 Subject: {subject}")

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode(errors="ignore")
                            break
                        except:
                            continue
            else:
                try:
                    body = msg.get_payload(decode=True).decode(errors="ignore")
                except:
                    body = "[Could not decode]"

            print(f"📄 Body:\n{body[:300]}")

            from_ = msg.get("From")
            message_id = msg.get("Message-ID", "").strip()
            date = msg.get("Date", "").strip()

            # Decode subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8", errors="ignore")

            # Extract body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode(errors="ignore")
                            break
                        except:
                            continue
            else:
                try:
                    body = msg.get_payload(decode=True).decode(errors="ignore")
                except:
                    body = "[Could not decode]"

            # Create message dict
            email_message = {
                "from": from_,
                "subject": subject,
                "body": body,
                "date": date,
                "message_id": message_id,
            }

            # Save to DB
            await save_email_to_db(session=db, email_message=email_message)


    imap.logout()

if __name__ == "__main__":
    asyncio.run(fetch_and_store_replies())
