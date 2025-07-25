from fastapi import FastAPI
from smtp_test import send_test_email
from imap_fetch_replies import fetch_replies

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "FastAPI is running"}

@app.post("/send-email")
def trigger_email():
    try:
        send_test_email()
        return {"status": "✅ Email sent"}
    except Exception as e:
        return {"status": "❌ Failed", "error": str(e)}

@app.get("/fetch-replies")
def trigger_reply_fetch():
    try:
        fetch_replies()
        return {"status": "✅ Replies fetched and saved"}
    except Exception as e:
        return {"status": "❌ Failed", "error": str(e)}
