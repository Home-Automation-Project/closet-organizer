from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.crud import crud
from app.schemas.schemas import WashReminderOut, SeasonalReminderOut, SeasonalReminderCreate

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("/wash", response_model=List[WashReminderOut])
async def list_wash_reminders(db: AsyncSession = Depends(get_db)):
    return await crud.get_active_wash_reminders(db)


@router.patch("/wash/{reminder_id}/acknowledge", response_model=WashReminderOut)
async def acknowledge_wash(reminder_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.acknowledge_wash_reminder(db, reminder_id)
    if not obj:
        raise HTTPException(404, "Reminder not found")
    return obj


@router.get("/seasonal", response_model=List[SeasonalReminderOut])
async def list_seasonal_reminders(db: AsyncSession = Depends(get_db)):
    return await crud.get_active_seasonal_reminders(db)


@router.post("/seasonal", response_model=SeasonalReminderOut, status_code=201)
async def create_seasonal_reminder(data: SeasonalReminderCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_seasonal_reminder(db, data)


@router.patch("/seasonal/{reminder_id}/acknowledge", response_model=SeasonalReminderOut)
async def acknowledge_seasonal(reminder_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.acknowledge_seasonal_reminder(db, reminder_id)
    if not obj:
        raise HTTPException(404, "Reminder not found")
    return obj
