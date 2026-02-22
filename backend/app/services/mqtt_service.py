"""
MQTT service — manages the paho client lifecycle and handles inbound messages.
The client is started/stopped from main.py's lifespan context.
"""
import json
import logging
import os
from datetime import timezone
from typing import Callable

import paho.mqtt.client as mqtt

from app.db.session import AsyncSessionLocal
from app.models.models import ShelfEventType
from app.crud import crud

logger = logging.getLogger(__name__)

_client: mqtt.Client | None = None


def _get_client() -> mqtt.Client:
    global _client
    if _client is None:
        raise RuntimeError("MQTT client not initialised")
    return _client


def publish(topic: str, payload: dict | str) -> None:
    msg = payload if isinstance(payload, str) else json.dumps(payload)
    _get_client().publish(topic, msg, qos=1)


# ---------------------------------------------------------------------------
# Inbound message handlers
# ---------------------------------------------------------------------------

def _handle_presence(shelf_id: int, payload: dict) -> None:
    import asyncio
    state = payload.get("state", "").lower()
    if state not in ("occupied", "empty"):
        logger.warning("Unknown presence state: %s", state)
        return

    async def _process():
        async with AsyncSessionLocal() as db:
            event_type = ShelfEventType.EMPTY if state == "empty" else ShelfEventType.OCCUPIED
            await crud.record_shelf_event(db, shelf_id, event_type)
            if event_type == ShelfEventType.EMPTY:
                reminder = await crud.create_wash_reminder(db, shelf_id)
                payload_out = {
                    "shelf_id": shelf_id,
                    "message": "Wash sheets within 24h",
                    "due_at": reminder.due_at.isoformat(),
                }
                publish("closet/alerts/wash_reminder", payload_out)
                logger.info("Wash reminder created for shelf %s", shelf_id)

    asyncio.run_coroutine_threadsafe(_process(), _get_event_loop())


def _handle_nfc_tap(basket_id: int, payload: dict) -> None:
    logger.info("NFC tap on basket %s — tag_id: %s", basket_id, payload.get("tag_id"))
    # The frontend handles display; we just log for now.


# ---------------------------------------------------------------------------
# paho callbacks
# ---------------------------------------------------------------------------

def _on_connect(client, userdata, flags, reason_code, properties=None):
    logger.info("MQTT connected (rc=%s)", reason_code)
    client.subscribe("closet/shelf/+/presence", qos=1)
    client.subscribe("closet/basket/+/nfc_tap", qos=1)


def _on_message(client, userdata, msg):
    try:
        topic_parts = msg.topic.split("/")
        payload = json.loads(msg.payload.decode())
        # closet/shelf/{shelf_id}/presence
        if len(topic_parts) == 4 and topic_parts[0] == "closet" and topic_parts[1] == "shelf" and topic_parts[3] == "presence":
            _handle_presence(int(topic_parts[2]), payload)
        # closet/basket/{basket_id}/nfc_tap
        elif len(topic_parts) == 4 and topic_parts[0] == "closet" and topic_parts[1] == "basket" and topic_parts[3] == "nfc_tap":
            _handle_nfc_tap(int(topic_parts[2]), payload)
        else:
            logger.debug("Unhandled topic: %s", msg.topic)
    except Exception as exc:
        logger.exception("Error processing MQTT message on %s: %s", msg.topic, exc)


# ---------------------------------------------------------------------------
# Public lifecycle helpers
# ---------------------------------------------------------------------------

_event_loop = None


def set_event_loop(loop):
    global _event_loop
    _event_loop = loop


def _get_event_loop():
    if _event_loop is None:
        raise RuntimeError("Event loop not registered with MQTT service")
    return _event_loop


def start(host: str, port: int) -> mqtt.Client:
    global _client
    _client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    _client.on_connect = _on_connect
    _client.on_message = _on_message
    _client.connect(host, port, keepalive=60)
    _client.loop_start()
    logger.info("MQTT client started — connecting to %s:%s", host, port)
    return _client


def stop() -> None:
    global _client
    if _client:
        _client.loop_stop()
        _client.disconnect()
        _client = None
        logger.info("MQTT client stopped")
