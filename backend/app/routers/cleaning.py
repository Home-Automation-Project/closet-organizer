import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.data_loader import DataLoader

router = APIRouter(prefix="/cleaning", tags=["cleaning"])


@router.get("/rooms")
async def list_rooms():
    """Get all cleaning rooms."""
    rooms = DataLoader.get_cleaning_rooms()
    return [room["id"] for room in rooms]


@router.get("/{room_type}")
async def get_room_checklist(
    room_type: str,
    session_token: Optional[str] = Query(default=None),
):
    """Get checklist for a room. Session token tracks completion in current session."""
    room = DataLoader.get_cleaning_room(room_type)
    if not room:
        raise HTTPException(404, f"Room '{room_type}' not found")
    
    token = session_token or str(uuid.uuid4())
    
    items = []
    for category in room.get("categories", []):
        for item in category.get("items", []):
            items.append({
                "key": item["key"],
                "description": item["description"],
                "frequency": item["frequency"],
                "category": category["category"],
                "sortOrder": item["sortOrder"]
            })
    
    return {
        "room_type": room_type,
        "items": items,
        "completions": [],
        "session_token": token,
    }


@router.post("/{room_type}/complete/{item_key}", status_code=201)
async def complete_item(
    room_type: str,
    item_key: str,
    session_token: str = Query(...),
):
    """Mark an item as complete in current session."""
    room = DataLoader.get_cleaning_room(room_type)
    if not room:
        raise HTTPException(404, f"Room '{room_type}' not found")
    
    return {
        "id": f"{session_token}_{item_key}",
        "room_type": room_type,
        "item_key": item_key,
        "session_token": session_token,
        "completed_at": str(__import__("datetime").datetime.now().isoformat())
    }


@router.delete("/{room_type}/complete/{item_key}", status_code=204)
async def uncomplete_item(
    room_type: str,
    item_key: str,
    session_token: str = Query(...),
):
    """Mark an item as incomplete in current session."""
    pass


@router.delete("/{room_type}/session", status_code=204)
async def reset_checklist_session(
    room_type: str,
    session_token: str = Query(...),
):
    """Reset/clear a cleaning session."""
    pass
