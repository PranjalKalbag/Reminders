from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncConnection
from models import reminders
from uuid import uuid4, UUID
from datetime import datetime
import schemas


async def create_reminder(conn: AsyncConnection, reminder: schemas.ReminderInput):
    new_id = uuid4()
    created_at = datetime.utcnow()
    await conn.execute(
        insert(reminders).values(
            id=new_id,
            created_at=created_at,
            title=reminder.title,
            description=reminder.description,
            rrule=reminder.rrule,
            start_date=reminder.start_date,
            end_date=reminder.end_date,
        )
    )
    return schemas.ReminderOut(id=new_id, created_at=created_at, **reminder.dict())

async def get_all_reminders(conn: AsyncConnection):
    result = await conn.execute(select(reminders))
    result = result.mappings().all()
    return [dict(row) for row in result]


async def get_reminder(conn: AsyncConnection, reminder_id: UUID):
    result = await conn.execute(select(reminders).where(reminders.c.id==reminder_id))
    result = result.fetchone()
    return dict(result._mapping) if result else None