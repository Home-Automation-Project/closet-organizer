import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import closets, inventory, reminders, cleaning, firstaid, family
from app.routers.closets import shelves_router, baskets_router

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
    logger.info("Closet Organizer API starting...")
    logger.info("Data sources: Static JSON + Google Sheets")

    yield

    # ------------------------------------------------------------------ #
    # SHUTDOWN
    # ------------------------------------------------------------------ #
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
