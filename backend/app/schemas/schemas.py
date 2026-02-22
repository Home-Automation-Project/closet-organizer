from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from app.models.models import (
    BasketType, ShelfEventType, ItemFrequency,
    ReminderCategory, QuantityStatus, ExpirationStatus, BasketStatus
)


# ---------------------------------------------------------------------------
# Closet
# ---------------------------------------------------------------------------

class ClosetBase(BaseModel):
    name: str
    location: Optional[str] = None


class ClosetCreate(ClosetBase):
    pass


class ClosetUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None


class ClosetOut(ClosetBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# ---------------------------------------------------------------------------
# Shelf
# ---------------------------------------------------------------------------

class ShelfBase(BaseModel):
    label: Optional[str] = None
    position_order: int = 0


class ShelfCreate(ShelfBase):
    closet_id: int


class ShelfUpdate(BaseModel):
    label: Optional[str] = None
    position_order: Optional[int] = None


class ShelfOut(ShelfBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    closet_id: int
    created_at: datetime


# ---------------------------------------------------------------------------
# Basket
# ---------------------------------------------------------------------------

class BasketBase(BaseModel):
    label: str
    basket_type: BasketType
    sub_bin: Optional[str] = None
    nfc_tag_id: Optional[str] = None
    position_order: int = 0


class BasketCreate(BasketBase):
    shelf_id: int


class BasketUpdate(BaseModel):
    label: Optional[str] = None
    basket_type: Optional[BasketType] = None
    sub_bin: Optional[str] = None
    nfc_tag_id: Optional[str] = None
    position_order: Optional[int] = None
    shelf_id: Optional[int] = None


class BasketOut(BasketBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    shelf_id: int
    qr_token: str
    created_at: datetime


class BasketWithStatus(BasketOut):
    status: BasketStatus


# ---------------------------------------------------------------------------
# Item Definition
# ---------------------------------------------------------------------------

class ItemDefinitionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    basket_type: BasketType
    sub_bin: Optional[str]
    name: str
    category: Optional[str]
    has_expiration: bool
    recommended_qty: int
    unit: Optional[str]


# ---------------------------------------------------------------------------
# Basket Inventory
# ---------------------------------------------------------------------------

class InventoryItemBase(BaseModel):
    quantity: int
    expiration_date: Optional[datetime] = None
    notes: Optional[str] = None


class InventoryItemCreate(InventoryItemBase):
    basket_id: int
    item_definition_id: int


class InventoryItemUpdate(BaseModel):
    quantity: Optional[int] = None
    expiration_date: Optional[datetime] = None
    notes: Optional[str] = None


class InventoryItemOut(InventoryItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    basket_id: int
    item_definition_id: int
    updated_at: datetime
    item_definition: ItemDefinitionOut


class InventoryItemWithStatus(InventoryItemOut):
    quantity_status: QuantityStatus
    expiration_status: ExpirationStatus


# ---------------------------------------------------------------------------
# Shelf Event / Wash Reminder
# ---------------------------------------------------------------------------

class ShelfEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    shelf_id: int
    event_type: ShelfEventType
    occurred_at: datetime


class WashReminderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    shelf_id: int
    triggered_at: datetime
    due_at: datetime
    acknowledged_at: Optional[datetime]


# ---------------------------------------------------------------------------
# Seasonal Reminder
# ---------------------------------------------------------------------------

class SeasonalReminderCreate(BaseModel):
    basket_id: Optional[int] = None
    category: ReminderCategory
    reminder_text: str
    due_date: Optional[datetime] = None


class SeasonalReminderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    basket_id: Optional[int]
    category: ReminderCategory
    reminder_text: str
    due_date: Optional[datetime]
    sent_at: Optional[datetime]
    created_at: datetime


# ---------------------------------------------------------------------------
# Cleaning Checklist
# ---------------------------------------------------------------------------

class ChecklistItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    room_type: str
    category: str
    item_key: str
    description: str
    frequency: ItemFrequency
    sort_order: int


class ChecklistCompletionCreate(BaseModel):
    room_type: str
    item_key: str
    session_token: str


class ChecklistCompletionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    room_type: str
    item_key: str
    session_token: str
    completed_at: datetime


class RoomChecklistOut(BaseModel):
    room_type: str
    items: List[ChecklistItemOut]
    completions: List[ChecklistCompletionOut]
    session_token: str


# ---------------------------------------------------------------------------
# Family Member
# ---------------------------------------------------------------------------

class FamilyMemberBase(BaseModel):
    name: str
    date_of_birth: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    medications: Optional[str] = None
    medical_conditions: Optional[str] = None
    emergency_contact: Optional[str] = None
    notes: Optional[str] = None


class FamilyMemberCreate(FamilyMemberBase):
    pass


class FamilyMemberUpdate(BaseModel):
    name: Optional[str] = None
    date_of_birth: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    medications: Optional[str] = None
    medical_conditions: Optional[str] = None
    emergency_contact: Optional[str] = None
    notes: Optional[str] = None


class FamilyMemberOut(FamilyMemberBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Aggregated dashboard payload
# ---------------------------------------------------------------------------

class BasketDetailOut(BasketWithStatus):
    inventory: List[InventoryItemWithStatus] = []


class ShelfDetailOut(ShelfOut):
    baskets: List[BasketWithStatus] = []


class ClosetDetailOut(ClosetOut):
    shelves: List[ShelfDetailOut] = []


# ---------------------------------------------------------------------------
# MQTT event payloads (incoming)
# ---------------------------------------------------------------------------

class PresencePayload(BaseModel):
    state: str  # "occupied" | "empty"


class NfcTapPayload(BaseModel):
    tag_id: str
