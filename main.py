from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from database import engine

import crud
from schemas import *
app = FastAPI()


@app.post("/input", response_model=ReminderInput)
async def new_reminder(reminder: ReminderInput):
    async with engine.begin() as conn:
        return await crud.create_reminder(conn, reminder)