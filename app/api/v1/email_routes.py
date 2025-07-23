from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db, AsyncSessionLocal
from app.db import models
from app.utils.logger import log_event
from email.message import EmailMessage
from aiosmtplib import SMTP
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables
load_dotenv()
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USERNAME")  # Changed from SMTP_USER to SMTP_USERNAME
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM")

router = APIRouter()

async def send_async_email(to_email: str, subject: str, body: str):
    """Send email asynchronously via aiosmtplib."""
    print(f"🔵 Attempting to send email to {to_email}")
    print(f"🔵 SMTP Config: {SMTP_HOST}:{SMTP_PORT}, User: {SMTP_USER}")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg.set_content(body)

    # Use SSL for port 465, STARTTLS for port 587
    use_tls = SMTP_PORT == 465
    smtp = SMTP(hostname=SMTP_HOST, port=SMTP_PORT, use_tls=use_tls, start_tls=(SMTP_PORT == 587), timeout=30)
    try:
        print("🔵 Connecting to SMTP server...")
        await smtp.connect()
        print("🔵 Logging in...")
        await smtp.login(SMTP_USER, SMTP_PASSWORD)
        print("🔵 Sending message...")
        await smtp.send_message(msg)
        print("🟢 Email sent successfully!")
    finally:
        try:
            await smtp.quit()
        except Exception:
            pass  # Ignore quit errors

@router.post("/send-emails")
async def send_pending_emails(db: AsyncSession = Depends(get_db)):
    print("🟢 /send-emails called")

    vendor_result = await db.execute(
        select(models.Vendor).where(models.Vendor.status == "Not started")
    )
    vendors =  vendor_result.scalars().all()

    if not vendors:
        await log_event(
            db=db,
            action="NoVendorsFound",
            details="No vendors with status 'Not started' to send emails.",
            source="send_pending_emails"
        )
        return {
            "status": "no vendors",
            "sent_count": 0,
            "failed_count": 0,
            "failed_vendors": [],
            "total_attempted": 0
        }

    sent_count = 0
    failed_vendors = []

    for vendor in vendors:
        # Store vendor data before any operations that might fail
        vendor_id = vendor.id
        vendor_name = vendor.vendor_name
        vendor_email = vendor.contact_email
        vendor_type = vendor.vendor_type
        vendor_notes = vendor.notes
        vendor_phone = vendor.phone_number
        vendor_status = vendor.status
        vendor_city = vendor.vendor_city
        vendor_services = vendor.vendor_services
        vendor_instagram = vendor.instagram_link
        vendor_created_by = vendor.created_by

        try:
            if not vendor_email:
                raise ValueError("Missing contact email")

            script_result = await db.execute(
                select(models.Script)
                .where(models.Script.category == vendor_type)
                .order_by(models.Script.step_number.asc())
            )
            script = script_result.scalars().first()

            if not script:
                raise ValueError(f"No script found for vendor_type: {vendor_type}")

            if not script.message:
                raise ValueError(f"Script message is empty for vendor_type: {vendor_type}")

            await send_async_email(
                to_email=vendor_email,
                subject=f"Partnership Opportunity - {vendor_name}",
                body=script.message
            )

            vendor.status = "sent"
            db.add(vendor)
            await db.commit()

            await log_event(
                db=db,
                action="EmailSent",
                details=f"Email sent to {vendor_email} using script ID {script.id}",
                source="send_pending_emails"
            )

            sent_count += 1
            await asyncio.sleep(2)

        except Exception as e:
            try:
                await db.rollback()
            except Exception:
                pass  # Ignore rollback errors

            try:
                # Create new session for failed mail entry to avoid greenlet issues
                async with AsyncSessionLocal() as new_db:
                    failed_vendor = models.FailedMail(
                        vendor_id=vendor_id,
                        vendor_name=vendor_name,
                        contact_email=vendor_email,
                        notes=vendor_notes,
                        phone_number=vendor_phone,
                        status=vendor_status,
                        vendor_city=vendor_city,
                        vendor_services=vendor_services,
                        vendor_type=vendor_type,
                        instagram_link=vendor_instagram,
                        created_by=vendor_created_by,
                        failed_reason=str(e),
                        created_at=datetime.now(timezone.utc)
                    )

                    new_db.add(failed_vendor)
                    await new_db.commit()

                    await log_event(
                        db=new_db,
                        action="SendError",
                        details=f"Failed to send email to {vendor_name}: {str(e)}",
                        source="send_pending_emails"
                    )
            except Exception as log_error:
                print(f"Failed to log error for vendor {vendor_name}: {log_error}")

            failed_vendors.append({
                "vendor": vendor_name,
                "reason": str(e)
            })
            continue

    return {
        "status": "completed",
        "sent_count": sent_count,
        "failed_count": len(failed_vendors),
        "failed_vendors": failed_vendors,
        "total_attempted": len(vendors)
    }
