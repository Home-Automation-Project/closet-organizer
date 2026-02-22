"""
Core CRUD helpers shared across routers.
All functions receive an AsyncSession and return ORM objects or None.
Status computation is done here so routers stay thin.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import (
    Basket, BasketInventory, BasketStatus, Closet, ExpirationStatus,
    FamilyMember, ItemDefinition, QuantityStatus, Shelf, ShelfEvent,
    ShelfEventType, WashReminder, SeasonalReminder, ChecklistItem,
    ChecklistCompletion,
)
from app.schemas.schemas import (
    BasketCreate, BasketUpdate, ClosetCreate, ClosetUpdate,
    InventoryItemCreate, InventoryItemUpdate,
    SeasonalReminderCreate, ShelfCreate, ShelfUpdate,
    FamilyMemberCreate, FamilyMemberUpdate,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(timezone.utc)


def compute_expiration_status(expiration_date: Optional[datetime]) -> ExpirationStatus:
    if expiration_date is None:
        return ExpirationStatus.NA
    now = _now()
    exp = expiration_date if expiration_date.tzinfo else expiration_date.replace(tzinfo=timezone.utc)
    if exp < now:
        return ExpirationStatus.EXPIRED
    if exp < now + timedelta(days=30):
        return ExpirationStatus.EXPIRING_SOON
    return ExpirationStatus.OK


def compute_quantity_status(quantity: int, recommended: int) -> QuantityStatus:
    if recommended == 0:
        return QuantityStatus.OK
    ratio = quantity / recommended
    if ratio < 0.5:
        return QuantityStatus.LOW
    if ratio > 1.5:
        return QuantityStatus.OVERSTOCKED
    return QuantityStatus.OK


def compute_basket_status(inventory_items: list[BasketInventory]) -> BasketStatus:
    has_yellow = False
    for item in inventory_items:
        exp = compute_expiration_status(item.expiration_date)
        if exp == ExpirationStatus.EXPIRED:
            return BasketStatus.RED
        qty = compute_quantity_status(item.quantity, item.item_definition.recommended_qty if item.item_definition else 1)
        if exp == ExpirationStatus.EXPIRING_SOON or qty == QuantityStatus.LOW:
            has_yellow = True
    return BasketStatus.YELLOW if has_yellow else BasketStatus.GREEN


# ---------------------------------------------------------------------------
# Closets
# ---------------------------------------------------------------------------

async def get_closets(db: AsyncSession) -> list[Closet]:
    result = await db.execute(select(Closet).order_by(Closet.id))
    return list(result.scalars().all())


async def get_closet(db: AsyncSession, closet_id: int) -> Optional[Closet]:
    result = await db.execute(
        select(Closet)
        .options(
            selectinload(Closet.shelves).selectinload(Shelf.baskets)
        )
        .where(Closet.id == closet_id)
    )
    return result.scalar_one_or_none()


async def create_closet(db: AsyncSession, data: ClosetCreate) -> Closet:
    obj = Closet(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update_closet(db: AsyncSession, closet_id: int, data: ClosetUpdate) -> Optional[Closet]:
    obj = await db.get(Closet, closet_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_closet(db: AsyncSession, closet_id: int) -> bool:
    obj = await db.get(Closet, closet_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True


# ---------------------------------------------------------------------------
# Shelves
# ---------------------------------------------------------------------------

async def get_shelves(db: AsyncSession, closet_id: int) -> list[Shelf]:
    result = await db.execute(
        select(Shelf).where(Shelf.closet_id == closet_id).order_by(Shelf.position_order)
    )
    return list(result.scalars().all())


async def get_shelf(db: AsyncSession, shelf_id: int) -> Optional[Shelf]:
    return await db.get(Shelf, shelf_id)


async def create_shelf(db: AsyncSession, data: ShelfCreate) -> Shelf:
    obj = Shelf(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update_shelf(db: AsyncSession, shelf_id: int, data: ShelfUpdate) -> Optional[Shelf]:
    obj = await db.get(Shelf, shelf_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_shelf(db: AsyncSession, shelf_id: int) -> bool:
    obj = await db.get(Shelf, shelf_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True


# ---------------------------------------------------------------------------
# Baskets
# ---------------------------------------------------------------------------

async def get_baskets(db: AsyncSession, shelf_id: int) -> list[Basket]:
    result = await db.execute(
        select(Basket).where(Basket.shelf_id == shelf_id).order_by(Basket.position_order)
    )
    return list(result.scalars().all())


async def get_basket(db: AsyncSession, basket_id: int) -> Optional[Basket]:
    result = await db.execute(
        select(Basket)
        .options(
            selectinload(Basket.inventory).selectinload(BasketInventory.item_definition)
        )
        .where(Basket.id == basket_id)
    )
    return result.scalar_one_or_none()


async def get_basket_by_qr(db: AsyncSession, qr_token: str) -> Optional[Basket]:
    result = await db.execute(
        select(Basket)
        .options(
            selectinload(Basket.inventory).selectinload(BasketInventory.item_definition)
        )
        .where(Basket.qr_token == qr_token)
    )
    return result.scalar_one_or_none()


async def get_basket_by_nfc(db: AsyncSession, nfc_tag_id: str) -> Optional[Basket]:
    result = await db.execute(
        select(Basket)
        .options(
            selectinload(Basket.inventory).selectinload(BasketInventory.item_definition)
        )
        .where(Basket.nfc_tag_id == nfc_tag_id)
    )
    return result.scalar_one_or_none()


async def create_basket(db: AsyncSession, data: BasketCreate) -> Basket:
    obj = Basket(**data.model_dump(), qr_token=str(uuid.uuid4()))
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update_basket(db: AsyncSession, basket_id: int, data: BasketUpdate) -> Optional[Basket]:
    obj = await db.get(Basket, basket_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_basket(db: AsyncSession, basket_id: int) -> bool:
    obj = await db.get(Basket, basket_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True


# ---------------------------------------------------------------------------
# Item Definitions
# ---------------------------------------------------------------------------

async def get_item_definitions(db: AsyncSession, basket_type=None, sub_bin=None) -> list[ItemDefinition]:
    q = select(ItemDefinition)
    if basket_type:
        q = q.where(ItemDefinition.basket_type == basket_type)
    if sub_bin:
        q = q.where(ItemDefinition.sub_bin == sub_bin)
    result = await db.execute(q.order_by(ItemDefinition.id))
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

async def get_inventory(db: AsyncSession, basket_id: int) -> list[BasketInventory]:
    result = await db.execute(
        select(BasketInventory)
        .options(selectinload(BasketInventory.item_definition))
        .where(BasketInventory.basket_id == basket_id)
    )
    return list(result.scalars().all())


async def upsert_inventory_item(
    db: AsyncSession, basket_id: int, item_definition_id: int, data: InventoryItemUpdate
) -> BasketInventory:
    result = await db.execute(
        select(BasketInventory)
        .where(BasketInventory.basket_id == basket_id)
        .where(BasketInventory.item_definition_id == item_definition_id)
    )
    obj = result.scalar_one_or_none()
    if obj is None:
        obj = BasketInventory(basket_id=basket_id, item_definition_id=item_definition_id)
        db.add(obj)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    # reload with definition
    result2 = await db.execute(
        select(BasketInventory)
        .options(selectinload(BasketInventory.item_definition))
        .where(BasketInventory.id == obj.id)
    )
    return result2.scalar_one()


async def delete_inventory_item(db: AsyncSession, inventory_id: int) -> bool:
    obj = await db.get(BasketInventory, inventory_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True


# ---------------------------------------------------------------------------
# Shelf Events + Wash Reminders
# ---------------------------------------------------------------------------

async def record_shelf_event(db: AsyncSession, shelf_id: int, event_type: ShelfEventType) -> ShelfEvent:
    event = ShelfEvent(shelf_id=shelf_id, event_type=event_type)
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def create_wash_reminder(db: AsyncSession, shelf_id: int) -> WashReminder:
    reminder = WashReminder(
        shelf_id=shelf_id,
        due_at=_now() + timedelta(hours=24),
    )
    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)
    return reminder


async def get_active_wash_reminders(db: AsyncSession) -> list[WashReminder]:
    result = await db.execute(
        select(WashReminder)
        .where(WashReminder.acknowledged_at.is_(None))
        .order_by(WashReminder.triggered_at.desc())
    )
    return list(result.scalars().all())


async def acknowledge_wash_reminder(db: AsyncSession, reminder_id: int) -> Optional[WashReminder]:
    obj = await db.get(WashReminder, reminder_id)
    if not obj:
        return None
    obj.acknowledged_at = _now()
    await db.commit()
    await db.refresh(obj)
    return obj


# ---------------------------------------------------------------------------
# Seasonal Reminders
# ---------------------------------------------------------------------------

async def get_active_seasonal_reminders(db: AsyncSession) -> list[SeasonalReminder]:
    result = await db.execute(
        select(SeasonalReminder)
        .where(SeasonalReminder.sent_at.is_(None))
        .order_by(SeasonalReminder.created_at.desc())
    )
    return list(result.scalars().all())


async def create_seasonal_reminder(db: AsyncSession, data: SeasonalReminderCreate) -> SeasonalReminder:
    obj = SeasonalReminder(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def acknowledge_seasonal_reminder(db: AsyncSession, reminder_id: int) -> Optional[SeasonalReminder]:
    obj = await db.get(SeasonalReminder, reminder_id)
    if not obj:
        return None
    obj.sent_at = _now()
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_expiring_items(db: AsyncSession, days: int = 30) -> list[BasketInventory]:
    cutoff = _now() + timedelta(days=days)
    result = await db.execute(
        select(BasketInventory)
        .options(selectinload(BasketInventory.item_definition))
        .where(BasketInventory.expiration_date.isnot(None))
        .where(BasketInventory.expiration_date <= cutoff)
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Cleaning Checklist
# ---------------------------------------------------------------------------

async def get_checklist_items(db: AsyncSession, room_type: str) -> list[ChecklistItem]:
    result = await db.execute(
        select(ChecklistItem)
        .where(ChecklistItem.room_type == room_type)
        .order_by(ChecklistItem.frequency, ChecklistItem.sort_order)
    )
    return list(result.scalars().all())


async def get_completions_for_session(db: AsyncSession, session_token: str) -> list[ChecklistCompletion]:
    result = await db.execute(
        select(ChecklistCompletion).where(ChecklistCompletion.session_token == session_token)
    )
    return list(result.scalars().all())


async def add_completion(
    db: AsyncSession, room_type: str, item_key: str, session_token: str
) -> ChecklistCompletion:
    obj = ChecklistCompletion(room_type=room_type, item_key=item_key, session_token=session_token)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def remove_completion(db: AsyncSession, session_token: str, item_key: str) -> bool:
    await db.execute(
        delete(ChecklistCompletion)
        .where(ChecklistCompletion.session_token == session_token)
        .where(ChecklistCompletion.item_key == item_key)
    )
    await db.commit()
    return True


async def reset_session(db: AsyncSession, session_token: str) -> None:
    await db.execute(
        delete(ChecklistCompletion).where(ChecklistCompletion.session_token == session_token)
    )
    await db.commit()


# ---------------------------------------------------------------------------
# Family Members
# ---------------------------------------------------------------------------

async def get_family_members(db: AsyncSession) -> list[FamilyMember]:
    result = await db.execute(select(FamilyMember).order_by(FamilyMember.name))
    return list(result.scalars().all())


async def get_family_member(db: AsyncSession, member_id: int) -> Optional[FamilyMember]:
    return await db.get(FamilyMember, member_id)


async def create_family_member(db: AsyncSession, data: FamilyMemberCreate) -> FamilyMember:
    obj = FamilyMember(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update_family_member(
    db: AsyncSession, member_id: int, data: FamilyMemberUpdate
) -> Optional[FamilyMember]:
    obj = await db.get(FamilyMember, member_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_family_member(db: AsyncSession, member_id: int) -> bool:
    obj = await db.get(FamilyMember, member_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True
