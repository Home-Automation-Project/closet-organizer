from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.crud import crud
from app.schemas.schemas import ItemDefinitionOut
from app.models.models import BasketType

router = APIRouter(prefix="/firstaid", tags=["firstaid"])

BASIC_KIT_SUB_BINS = None  # flat list, no sub-bins for basic kit

ADVANCED_SUB_BINS = [
    "TRAUMA", "WOUND", "AIRWAY", "BURN", "IMMOB",
    "MEDS", "DX", "PROCEDURE", "PPE", "DOCS",
    "WATER", "COMFORT",
]


@router.get("/kit/basic", response_model=List[ItemDefinitionOut])
async def get_basic_kit(
    category: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    items = await crud.get_item_definitions(db, basket_type=BasketType.FIRST_AID_BASIC)
    if category:
        items = [i for i in items if i.category == category]
    return items


@router.get("/kit/advanced/bins", response_model=List[str])
async def list_advanced_bins():
    return ADVANCED_SUB_BINS


@router.get("/kit/advanced", response_model=List[ItemDefinitionOut])
async def get_advanced_kit(
    sub_bin: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_item_definitions(
        db, basket_type=BasketType.FIRST_AID_ADVANCED, sub_bin=sub_bin
    )


@router.get("/cpr")
async def get_cpr_steps():
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
