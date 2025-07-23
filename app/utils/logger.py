from sqlalchemy.ext.asyncio import AsyncSession
from app.db import models
from datetime import datetime

async def log_event(db: AsyncSession, action: str, details: str, source: str):
    log_entry = models.LogEntry(
        action=action,
        details=details,
        source=source,
        created_at=datetime.utcnow()
    )
    db.add(log_entry)
    await db.commit()
