from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import text
from uuid import UUID
from datetime import date
from typing import Optional

import crud
from database import engine
from schemas import *
from ai import llm
from scheduler import start_scheduler, send_due_reminders


app = FastAPI()

@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.get("/")
@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/input", response_model=ReminderInput)
async def new_reminder(reminder: ReminderInput):
    
    desc = reminder.description
    rrule = llm.create_rrule(desc)
    if rrule.upper()!='NA':
        reminder.rrule = rrule
        async with engine.begin() as conn:
            return await crud.create_reminder(conn, reminder)
    
@app.get("/reminders", response_model=list[ReminderOut])
async def list_reminders():
    async with engine.connect() as conn:
        return await crud.get_all_reminders(conn)
    
@app.get('/reminders/search',response_model=list[ReminderOut])
async def search_by_date(date_: Optional[date] = Query(None, alias="date"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),):
    if not date_ and not (start_date and end_date):
        raise HTTPException(status_code=400, detail="You must provide either 'date' or both 'start_date' and 'end_date'")

    async with engine.connect() as conn:
        if date_:
            return await crud.get_reminders_by_date(conn, date_)
        else:
            return await crud.get_reminders_by_range(conn, start_date, end_date)

@app.get("/reminders/{reminder_id}", response_model=ReminderOut)
async def get_reminder(reminder_id: UUID):
    async with engine.connect() as conn:
        reminder = await crud.get_reminder(conn, reminder_id)
        if not reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        return reminder
    

