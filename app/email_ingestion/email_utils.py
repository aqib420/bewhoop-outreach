from app.db.models import Chat
from sqlalchemy.future import select
from email.utils import parseaddr
from datetime import datetime


# --- 🔧 Normalize the "from" field to extract just the email address
def normalize_email_address(raw_from):
    return parseaddr(raw_from)[1].lower()


# --- 💾 Save incoming email to DB
async def save_email_to_db(session, email_message):
    # 1. Normalize the sender's email
    user_id = normalize_email_address(email_message["from"])
    
    # 2. Extract other relevant fields
    message_id = email_message["message_id"]
    message_body = email_message["body"]
    timestamp = datetime.utcnow().isoformat()

    # 3. Check if chat already exists for this user
    result = await session.execute(select(Chat).filter(Chat.user_id == user_id))
    existing_chat = result.scalars().first()

    if existing_chat:
        # 4. Avoid duplicates using message_id
        if message_id not in (existing_chat.message_ids or []):
            print(f"✅ Appending message for existing user: {user_id}")
            existing_chat.messages.append({
                "role": "user",
                "content": message_body,
                "timestamp": timestamp
            })
            existing_chat.message_ids.append(message_id)
            await session.commit()
        else:
            print(f"🚫 Duplicate message for {user_id}, skipping.")
    else:
        # 5. Create a new chat for first-time sender
        print(f"🆕 Creating new chat for: {user_id}")
        new_chat = Chat(
            user_id=user_id,
            platform="email",
            messages=[{
                "role": "user",
                "content": message_body,
                "timestamp": timestamp
            }],
            message_ids=[message_id]
        )
        session.add(new_chat)
        await session.commit()
