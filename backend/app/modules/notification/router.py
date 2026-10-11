# backend/app/modules/notification/router.py
# LifeLink AI — Notification Module Router with Real-Time WebSockets
# Architecture Reference: ARCHITECTURE.md Section 22 (Module Breakdown)

from __future__ import annotations

import datetime
from typing import Any
import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.modules.notification.websocket import ws_manager

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.websocket("/ws/{channel}")
async def websocket_channel_endpoint(websocket: WebSocket, channel: str) -> None:
    """
    Subscribes client to real-time events for a specific channel
    (e.g., 'hospital', 'donor', 'general', or emergency requisition ID).
    """
    await ws_manager.connect(websocket, channel)
    try:
        # Send initial confirmation handshake
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "channel": channel,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "message": f"Subscribed to real-time LifeLink AI events for channel '{channel}'",
        })

        while True:
            # Keep connection alive; process client pings or heartbeat messages
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel)
    except Exception as e:
        logger.warning("websocket_exception", channel=channel, error=str(e))
        ws_manager.disconnect(websocket, channel)


@router.get("/health", summary="Notification service health")
async def notification_health() -> dict[str, Any]:
    return {
        "success": True,
        "service": "notifications",
        "websocket_active_channels": len(ws_manager._channels),
    }
