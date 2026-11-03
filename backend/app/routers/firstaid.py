from typing import Optional
from fastapi import APIRouter, Query, HTTPException

from app.data_loader import DataLoader

router = APIRouter(prefix="/firstaid", tags=["firstaid"])


@router.get("/kit/basic")
async def get_basic_kit(category: Optional[str] = Query(default=None)):
    """Get basic first aid kit items."""
    items = DataLoader.get_first_aid_basic_items()
    if category:
        items = [i for i in items if i.get("category") == category]
    return items


@router.get("/kit/advanced/bins")
async def list_advanced_bins():
    """Get list of advanced first aid kit bins."""
    bins = DataLoader.get_first_aid_advanced_bins()
    return [{"id": b["id"], "label": b["label"]} for b in bins]


@router.get("/kit/advanced")
async def get_advanced_kit(sub_bin: Optional[str] = Query(default=None)):
    """Get advanced first aid kit items, optionally filtered by sub-bin."""
    items = DataLoader.get_first_aid_advanced_items(sub_bin)
    return items


@router.get("/cpr")
async def get_cpr_steps():
    """Get CPR steps and emergency information."""
    return {
        "title": "CPR Steps",
        "poison_control": "1-800-222-1222",
        "steps": [
            {"step": 1, "title": "Check the scene", "detail": "Ensure the scene is safe for you and the victim."},
            {"step": 2, "title": "Check responsiveness", "detail": "Tap shoulders firmly and shout 'Are you OK?'"},
            {"step": 3, "title": "Call 911", "detail": "Call or have someone else call 911 immediately."},
            {"step": 4, "title": "Open the airway", "detail": "Tilt head back, lift chin to open airway."},
            {"step": 5, "title": "Check for breathing", "detail": "Look, listen, and feel for normal breathing for no more than 10 seconds."},
            {"step": 6, "title": "Begin chest compressions", "detail": "30 compressions: push hard and fast in centre of chest, at least 2 inches deep, 100–120 per minute."},
            {"step": 7, "title": "Give rescue breaths", "detail": "2 rescue breaths (1 second each). Watch for chest rise. Resume compressions immediately."},
            {"step": 8, "title": "Use AED when available", "detail": "Power on AED, attach pads, follow prompts. Resume CPR immediately after shock."},
            {"step": 9, "title": "Continue until help arrives", "detail": "Keep 30:2 ratio until trained responders take over or victim starts breathing."},
        ],
    }
