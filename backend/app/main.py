import asyncio
import logging
import os
import subprocess
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import closets, inventory, reminders, cleaning, firstaid, family
from app.routers.closets import shelves_router, baskets_router
from app.services import mqtt_service, reminder_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s  %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ------------------------------------------------------------------ #
    # STARTUP
    # ------------------------------------------------------------------ #
    logger.info("Running Alembic migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=os.path.dirname(os.path.dirname(__file__)),  # /app (backend root)
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.error("Alembic migration failed:\n%s", result.stderr)
        raise RuntimeError("Database migration failed")
    logger.info("Migrations complete:\n%s", result.stdout)

    # Run DB seed (idempotent)
    from app.seed import run_seed
    await run_seed()

    # Start MQTT
    mqtt_host = os.environ.get("MQTT_BROKER_HOST", "localhost")
    mqtt_port = int(os.environ.get("MQTT_BROKER_PORT", 1883))
    mqtt_service.set_event_loop(asyncio.get_event_loop())
    mqtt_service.start(mqtt_host, mqtt_port)

    # Start scheduler
    reminder_service.start()

    yield

    # ------------------------------------------------------------------ #
    # SHUTDOWN
    # ------------------------------------------------------------------ #
    reminder_service.stop()
    mqtt_service.stop()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Closet Organizer API",
    version="1.0.0",
    description="Home automation closet management system",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
PREFIX = "/api"

app.include_router(closets.router, prefix=PREFIX)
app.include_router(shelves_router, prefix=PREFIX)
app.include_router(baskets_router, prefix=PREFIX)
app.include_router(inventory.router, prefix=PREFIX)
app.include_router(reminders.router, prefix=PREFIX)
app.include_router(cleaning.router, prefix=PREFIX)
app.include_router(firstaid.router, prefix=PREFIX)
app.include_router(family.router, prefix=PREFIX)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
