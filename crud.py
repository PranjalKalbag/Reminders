from sqlalchemy import select, insert, update, delete, and_, or_
from sqlalchemy.ext.asyncio import AsyncConnection
from models import reminders
from uuid import uuid4, UUID
from datetime import datetime
import schemas
from utils import matches_rrule, rrule_matches_range

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

async def get_reminders_by_date(conn: AsyncConnection, target_date: datetime.date):
    result = await conn.execute(
        select(reminders).where(
            and_(
                reminders.c.start_date <= target_date,
                or_(
                    reminders.c.end_date == None,
                    reminders.c.end_date >= target_date
                )
            )
        )
    )
    raw_rows = result.fetchall()
    matches = []
    for row in raw_rows:
        data = dict(row._mapping)
        if matches_rrule(data["rrule"], data["start_date"], target_date):
            matches.append(schemas.ReminderOut(**data))
    return matches

async def get_reminders_by_range(conn: AsyncConnection, start_date: datetime.date, end_date: datetime.date):
    result = await conn.execute(
        select(reminders).where(
            reminders.c.start_date <= end_date,
            or_(
                reminders.c.end_date == None,
                reminders.c.end_date >= start_date
            )
        )
    )
    raw_rows = result.fetchall()
    matches = []
    for row in raw_rows:
        data = dict(row._mapping)
        if rrule_matches_range(data["rrule"], data["start_date"], start_date, end_date):
            matches.append(schemas.ReminderOut(**data))
    return matches
