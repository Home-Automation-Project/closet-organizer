"""
Scheduler service — APScheduler AsyncIOScheduler with persistent SQLAlchemy job store.
Jobs handle wash reminders, expiry checks, and seasonal cleaning notices.
"""
import logging
import os
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from app.db.session import AsyncSessionLocal
from app.crud import crud
from app.models.models import ReminderCategory
from app.schemas.schemas import SeasonalReminderCreate

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        raise RuntimeError("Scheduler not initialised")
    return _scheduler


# ---------------------------------------------------------------------------
# Job functions
# ---------------------------------------------------------------------------

async def _check_overdue_wash_reminders():
    """Republish MQTT alert for overdue wash reminders."""
    from app.services import mqtt_service
    now = datetime.now(timezone.utc)
    async with AsyncSessionLocal() as db:
        reminders = await crud.get_active_wash_reminders(db)
        for r in reminders:
            due = r.due_at if r.due_at.tzinfo else r.due_at.replace(tzinfo=timezone.utc)
            if due <= now:
                mqtt_service.publish(
                    "closet/alerts/wash_reminder",
                    {
                        "shelf_id": r.shelf_id,
                        "reminder_id": r.id,
                        "message": "OVERDUE: Wash sheets now!",
                        "due_at": r.due_at.isoformat(),
                    },
                )
                logger.info("Re-published overdue wash reminder id=%s", r.id)


async def _check_expiring_items():
    """Create seasonal reminders for any inventory items expiring within 30 days."""
    from app.services import mqtt_service
    async with AsyncSessionLocal() as db:
        items = await crud.get_expiring_items(db, days=30)
        for item in items:
            # Avoid duplicate reminders — check if one already exists
            active = await crud.get_active_seasonal_reminders(db)
            already_sent = any(
                r.reminder_text.startswith(f"Item expiring:")
                and f"item_id={item.id}" in r.reminder_text
                for r in active
            )
            if already_sent:
                continue

            text = (
                f"Item expiring: {item.item_definition.name} "
                f"(qty: {item.quantity}) — due {item.expiration_date.date().isoformat()} "
                f"[item_id={item.id}]"
            )
            reminder = await crud.create_seasonal_reminder(
                db,
                SeasonalReminderCreate(
                    basket_id=item.basket_id,
                    category=ReminderCategory.FIRST_AID,
                    reminder_text=text,
                    due_date=item.expiration_date,
                ),
            )
            mqtt_service.publish(
                "closet/alerts/expiring_item",
                {
                    "basket_id": item.basket_id,
                    "item": item.item_definition.name,
                    "expires_at": item.expiration_date.isoformat(),
                    "reminder_id": reminder.id,
                },
            )
            logger.info("Expiring item reminder created: %s", item.item_definition.name)


async def _send_seasonal_cleaning_reminders():
    """
    Quarterly job — creates standard cleaning supply reminders.
    In a real deployment you'd have a table of scheduled seasonal texts;
    here we seed a few representative ones.
    """
    from app.services import mqtt_service
    reminders_text = [
        "Replace kitchen and bathroom sponges",
        "Refill floor cleaner bottles",
        "Check all spray bottle nozzles for clogs",
        "Inspect cleaning supply expiry dates",
        "Restock microfibre cloths",
    ]
    async with AsyncSessionLocal() as db:
        for text in reminders_text:
            reminder = await crud.create_seasonal_reminder(
                db,
                SeasonalReminderCreate(
                    category=ReminderCategory.CLEANING,
                    reminder_text=text,
                ),
            )
            mqtt_service.publish(
                "closet/alerts/seasonal",
                {
                    "category": "CLEANING",
                    "message": text,
                    "reminder_id": reminder.id,
                },
            )
    logger.info("Seasonal cleaning reminders sent")


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

def start() -> AsyncIOScheduler:
    global _scheduler
    apscheduler_url = os.environ.get("APSCHEDULER_DB_URL")
    jobstores = {}
    if apscheduler_url:
        jobstores["default"] = SQLAlchemyJobStore(url=apscheduler_url)

    _scheduler = AsyncIOScheduler(jobstores=jobstores if jobstores else None)

    _scheduler.add_job(
        _check_overdue_wash_reminders,
        "interval",
        hours=1,
        id="overdue_wash_check",
        replace_existing=True,
        coalesce=True,
        misfire_grace_time=300,
    )
    _scheduler.add_job(
        _check_expiring_items,
        "cron",
        hour=2,
        minute=0,
        id="expiry_check",
        replace_existing=True,
        coalesce=True,
    )
    _scheduler.add_job(
        _send_seasonal_cleaning_reminders,
        "cron",
        month="1,4,7,10",
        day=1,
        hour=8,
        id="seasonal_cleaning",
        replace_existing=True,
        coalesce=True,
    )

    _scheduler.start()
    logger.info("APScheduler started with %d jobs", len(_scheduler.get_jobs()))
    return _scheduler


def stop() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("APScheduler stopped")
