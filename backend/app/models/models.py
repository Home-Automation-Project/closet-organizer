import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text,
    func, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BasketType(str, enum.Enum):
    BEDDING = "BEDDING"
    CLEANING = "CLEANING"
    FIRST_AID_BASIC = "FIRST_AID_BASIC"
    FIRST_AID_ADVANCED = "FIRST_AID_ADVANCED"


class ShelfEventType(str, enum.Enum):
    OCCUPIED = "OCCUPIED"
    EMPTY = "EMPTY"


class ItemFrequency(str, enum.Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    SEASONAL = "SEASONAL"


class ReminderCategory(str, enum.Enum):
    CLEANING = "CLEANING"
    FIRST_AID = "FIRST_AID"
    BEDDING = "BEDDING"


class QuantityStatus(str, enum.Enum):
    LOW = "LOW"
    OK = "OK"
    OVERSTOCKED = "OVERSTOCKED"


class ExpirationStatus(str, enum.Enum):
    EXPIRED = "EXPIRED"
    EXPIRING_SOON = "EXPIRING_SOON"
    OK = "OK"
    NA = "NA"


class BasketStatus(str, enum.Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


# ---------------------------------------------------------------------------
# Closet / Shelf / Basket
# ---------------------------------------------------------------------------

class Closet(Base):
    __tablename__ = "closets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    shelves: Mapped[list["Shelf"]] = relationship(
        "Shelf", back_populates="closet", cascade="all, delete-orphan",
        order_by="Shelf.position_order"
    )


class Shelf(Base):
    __tablename__ = "shelves"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    closet_id: Mapped[int] = mapped_column(ForeignKey("closets.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[Optional[str]] = mapped_column(String(120))
    position_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    closet: Mapped["Closet"] = relationship("Closet", back_populates="shelves")
    baskets: Mapped[list["Basket"]] = relationship(
        "Basket", back_populates="shelf", cascade="all, delete-orphan",
        order_by="Basket.position_order"
    )
    events: Mapped[list["ShelfEvent"]] = relationship(
        "ShelfEvent", back_populates="shelf", cascade="all, delete-orphan"
    )
    wash_reminders: Mapped[list["WashReminder"]] = relationship(
        "WashReminder", back_populates="shelf", cascade="all, delete-orphan"
    )


class Basket(Base):
    __tablename__ = "baskets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shelf_id: Mapped[int] = mapped_column(ForeignKey("shelves.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    basket_type: Mapped[BasketType] = mapped_column(Enum(BasketType), nullable=False)
    sub_bin: Mapped[Optional[str]] = mapped_column(String(60))  # e.g. TRAUMA, WOUND for advanced FA
    nfc_tag_id: Mapped[Optional[str]] = mapped_column(String(200), unique=True)
    qr_token: Mapped[str] = mapped_column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    position_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    shelf: Mapped["Shelf"] = relationship("Shelf", back_populates="baskets")
    inventory: Mapped[list["BasketInventory"]] = relationship(
        "BasketInventory", back_populates="basket", cascade="all, delete-orphan"
    )
    cleaning_logs: Mapped[list["CleaningLog"]] = relationship(
        "CleaningLog", back_populates="basket", cascade="all, delete-orphan"
    )
    seasonal_reminders: Mapped[list["SeasonalReminder"]] = relationship(
        "SeasonalReminder", back_populates="basket", cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# Item Definitions (catalog / seed data)
# ---------------------------------------------------------------------------

class ItemDefinition(Base):
    __tablename__ = "item_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    basket_type: Mapped[BasketType] = mapped_column(Enum(BasketType), nullable=False)
    sub_bin: Mapped[Optional[str]] = mapped_column(String(60))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(120))
    has_expiration: Mapped[bool] = mapped_column(Boolean, default=False)
    recommended_qty: Mapped[int] = mapped_column(Integer, default=1)
    unit: Mapped[Optional[str]] = mapped_column(String(60))

    inventory_entries: Mapped[list["BasketInventory"]] = relationship(
        "BasketInventory", back_populates="item_definition"
    )


# ---------------------------------------------------------------------------
# Basket Inventory
# ---------------------------------------------------------------------------

class BasketInventory(Base):
    __tablename__ = "basket_inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    basket_id: Mapped[int] = mapped_column(ForeignKey("baskets.id", ondelete="CASCADE"), nullable=False)
    item_definition_id: Mapped[int] = mapped_column(ForeignKey("item_definitions.id", ondelete="CASCADE"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    expiration_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    basket: Mapped["Basket"] = relationship("Basket", back_populates="inventory")
    item_definition: Mapped["ItemDefinition"] = relationship("ItemDefinition", back_populates="inventory_entries")


# ---------------------------------------------------------------------------
# Shelf Events + Wash Reminders (Bedding)
# ---------------------------------------------------------------------------

class ShelfEvent(Base):
    __tablename__ = "shelf_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shelf_id: Mapped[int] = mapped_column(ForeignKey("shelves.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[ShelfEventType] = mapped_column(Enum(ShelfEventType), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    shelf: Mapped["Shelf"] = relationship("Shelf", back_populates="events")


class WashReminder(Base):
    __tablename__ = "wash_reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shelf_id: Mapped[int] = mapped_column(ForeignKey("shelves.id", ondelete="CASCADE"), nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    shelf: Mapped["Shelf"] = relationship("Shelf", back_populates="wash_reminders")


# ---------------------------------------------------------------------------
# Cleaning
# ---------------------------------------------------------------------------

class CleaningLog(Base):
    __tablename__ = "cleaning_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    basket_id: Mapped[Optional[int]] = mapped_column(ForeignKey("baskets.id", ondelete="SET NULL"))
    room_type: Mapped[str] = mapped_column(String(80), nullable=False)
    cleaned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    checklist_snapshot: Mapped[Optional[dict]] = mapped_column(JSON)

    basket: Mapped[Optional["Basket"]] = relationship("Basket", back_populates="cleaning_logs")


class SeasonalReminder(Base):
    __tablename__ = "seasonal_reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    basket_id: Mapped[Optional[int]] = mapped_column(ForeignKey("baskets.id", ondelete="SET NULL"))
    category: Mapped[ReminderCategory] = mapped_column(Enum(ReminderCategory), nullable=False)
    reminder_text: Mapped[str] = mapped_column(String(500), nullable=False)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    basket: Mapped[Optional["Basket"]] = relationship("Basket", back_populates="seasonal_reminders")


# ---------------------------------------------------------------------------
# Cleaning Checklist Completions
# ---------------------------------------------------------------------------

class ChecklistItem(Base):
    """Static catalog of per-room cleaning checklist items."""
    __tablename__ = "checklist_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_type: Mapped[str] = mapped_column(String(80), nullable=False)
    category: Mapped[str] = mapped_column(String(120))
    item_key: Mapped[str] = mapped_column(String(200), nullable=False)  # unique slug
    description: Mapped[str] = mapped_column(String(400), nullable=False)
    frequency: Mapped[ItemFrequency] = mapped_column(Enum(ItemFrequency), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class ChecklistCompletion(Base):
    """Records a single item being checked off during a cleaning session."""
    __tablename__ = "checklist_completions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_type: Mapped[str] = mapped_column(String(80), nullable=False)
    item_key: Mapped[str] = mapped_column(String(200), nullable=False)
    session_token: Mapped[str] = mapped_column(String(36), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ---------------------------------------------------------------------------
# Family Medical Info (First Aid section)
# ---------------------------------------------------------------------------

class FamilyMember(Base):
    __tablename__ = "family_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    date_of_birth: Mapped[Optional[str]] = mapped_column(String(20))
    blood_type: Mapped[Optional[str]] = mapped_column(String(10))
    allergies: Mapped[Optional[str]] = mapped_column(Text)
    medications: Mapped[Optional[str]] = mapped_column(Text)
    medical_conditions: Mapped[Optional[str]] = mapped_column(Text)
    emergency_contact: Mapped[Optional[str]] = mapped_column(String(200))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
