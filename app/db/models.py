from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.db.base import Base

class LogEntry(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)              # e.g., "EmailSent", "VendorUpdated"
    details = Column(Text, nullable=True)                     # Optional JSON string or message
    source = Column(String(100), nullable=True)               # e.g., "send_pending_emails"
    created_at = Column(DateTime, default=datetime.utcnow)

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    vendor_name = Column(String, nullable=False)
    contact_email = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    phone_number = Column(String, nullable=True)
    status = Column(String, default="Not started")
    vendor_city = Column(String, nullable=True)
    vendor_services = Column(Text, nullable=True)
    vendor_type = Column(String, nullable=True)
    instagram_link = Column(String, nullable=True)
    created_by = Column(String, nullable=True)


class Script(Base):
    __tablename__ = "scripts"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)  # e.g., "Event Lead"
    step_number = Column(Integer, nullable=False)  # step 1, 2, 3...
    message = Column(Text, nullable=False)
    triggers = Column(ARRAY(String))  # trigger words from response
    created_at = Column(DateTime, default=datetime.utcnow)

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)  # WhatsApp number, email, etc.
    platform = Column(String, nullable=False)  # e.g., "WhatsApp", "Email"
    messages = Column(JSONB, default=list)  # full message history
    current_step = Column(Integer, default=1)
    tags = Column(ARRAY(String), default=list)  # optional
    is_escalated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # NEW FIELD for deduplication
    message_ids = Column(ARRAY(String), default=list)

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    contact_info = Column(JSONB, nullable=False)  # {"email": "...", "phone": "..."}
    category = Column(String, nullable=False)
    escalated = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class KnowledgeEntry(Base):
    __tablename__ = "knowledge_entries"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    embedding = Column(ARRAY(Float), nullable=False)
    category = Column(String, nullable=False)

class FailedMail(Base):
    __tablename__ = "failed_mails"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer)
    vendor_name = Column(String, nullable=False)
    contact_email = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    phone_number = Column(String, nullable=True)
    status = Column(String)
    vendor_city = Column(String, nullable=True)
    vendor_services = Column(Text, nullable=True)
    vendor_type = Column(String, nullable=True)
    instagram_link = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    failed_reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
