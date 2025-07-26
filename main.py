from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from database import engine
from uuid import UUID

import crud
from schemas import *

app = FastAPI()


@app.post("/input", response_model=ReminderInput)
async def new_reminder(reminder: ReminderInput):
    async with engine.begin() as conn:
        return await crud.create_reminder(conn, reminder)
    
@app.get("/reminders", response_model=list[ReminderOut])
async def list_reminders():
    async with engine.connect() as conn:
        return await crud.get_all_reminders(conn)
    
@app.get("/reminders/{reminder_id}", response_model=ReminderOut)
async def get_reminder(reminder_id: UUID):
    async with engine.connect() as conn:
        reminder = await crud.get_reminder(conn, reminder_id)
        if not reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        return reminder