from fastapi import APIRouter, HTTPException

from app.services.gsheets_service import GoogleSheetsAdapter

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("/wash")
async def list_wash_reminders():
    """Get all wash (bedding) reminders from Google Sheets."""
    reminders = GoogleSheetsAdapter.get_reminders("BEDDING")
    return reminders


@router.patch("/wash/{reminder_id}/acknowledge", status_code=200)
async def acknowledge_wash(reminder_id: str):
    """Acknowledge a wash reminder in Google Sheets."""
    result = GoogleSheetsAdapter.acknowledge_reminder(reminder_id)
    return result


@router.get("/seasonal")
async def list_seasonal_reminders():
    """Get all seasonal reminders from Google Sheets."""
    reminders = GoogleSheetsAdapter.get_reminders()
    return reminders


@router.post("/seasonal", status_code=201)
async def create_seasonal_reminder(data: dict):
    """Create a new seasonal reminder in Google Sheets."""
    result = GoogleSheetsAdapter.create_reminder(
        data.get("category", "CLEANING"),
        data.get("reminder_text", ""),
        data.get("due_date")
    )
    return result


@router.patch("/seasonal/{reminder_id}/acknowledge", status_code=200)
async def acknowledge_seasonal(reminder_id: str):
    """Acknowledge a seasonal reminder in Google Sheets."""
    result = GoogleSheetsAdapter.acknowledge_reminder(reminder_id)
    return result
