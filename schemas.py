import uuid

from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class ReminderInput(BaseModel):
    title: str
    description: str
    rrule: str
    start_date: date
    end_date: Optional[date]


class ReminderUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    rrule: Optional[str]
    start_date: date
    end_date: Optional[date]

class ReminderOut(ReminderInput):
    id: uuid.UUID
    created_at: datetime
