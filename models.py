from sqlalchemy import Table, Column, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from database import metadata

reminders = Table(
    "reminders",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("created_at", TIMESTAMP(timezone=True)),
    Column("title", String, nullable=False),
    Column("description", String),
    Column("rrule", String, nullable=False),
    Column("start_date", TIMESTAMP(timezone=True), nullable=False),
    Column("end_date", TIMESTAMP(timezone=True)),
)


