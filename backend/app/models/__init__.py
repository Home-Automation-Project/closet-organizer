from app.models.models import (  # noqa: F401 — ensures models are registered with Base.metadata
    Closet, Shelf, Basket, ItemDefinition, BasketInventory,
    ShelfEvent, WashReminder, CleaningLog, SeasonalReminder,
    ChecklistItem, ChecklistCompletion, FamilyMember
)
