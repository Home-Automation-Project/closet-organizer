import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.crud import crud
from app.schemas.schemas import (
    ChecklistItemOut, ChecklistCompletionOut, RoomChecklistOut,
)

router = APIRouter(prefix="/cleaning", tags=["cleaning"])

ROOMS = [
    "library", "kitchen", "dining_room", "gym", "bedroom",
    "bathroom", "playroom", "hallways", "laundry_room", "garage", "family_room"
]


@router.get("/rooms", response_model=List[str])
async def list_rooms():
    return ROOMS


@router.get("/{room_type}", response_model=RoomChecklistOut)
async def get_room_checklist(
    room_type: str,
    session_token: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    if room_type not in ROOMS:
        raise HTTPException(404, f"Room '{room_type}' not found")
    # Generate a new session token if not provided (first visit via QR scan)
    token = session_token or str(uuid.uuid4())
    items = await crud.get_checklist_items(db, room_type)
    completions = await crud.get_completions_for_session(db, token)
    return RoomChecklistOut(
        room_type=room_type,
        items=items,
        completions=completions,
        session_token=token,
    )


@router.post("/{room_type}/complete/{item_key}", response_model=ChecklistCompletionOut, status_code=201)
async def complete_item(
    room_type: str,
    item_key: str,
    session_token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    if room_type not in ROOMS:
        raise HTTPException(404, f"Room '{room_type}' not found")
    return await crud.add_completion(db, room_type, item_key, session_token)


@router.delete("/{room_type}/complete/{item_key}", status_code=204)
async def uncomplete_item(
    room_type: str,
    item_key: str,
    session_token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    await crud.remove_completion(db, session_token, item_key)


@router.delete("/{room_type}/session", status_code=204)
async def reset_checklist_session(
    room_type: str,
    session_token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    await crud.reset_session(db, session_token)
