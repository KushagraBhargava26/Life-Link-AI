# backend/app/modules/notification/websocket.py
# LifeLink AI — Real-Time WebSocket Connection & Event Broadcast Manager
# Architecture Reference: ARCHITECTURE.md Section 16 & Section 22

from __future__ import annotations

import json
from typing import Any, Dict, List, Set
import structlog
from fastapi import WebSocket

logger = structlog.get_logger(__name__)


class WebSocketConnectionManager:
    """
    Manages active WebSocket connections across client channels (hospital, donor, emergency tracking).
    Provides resilient multi-channel fan-out broadcasting for critical healthcare events.
    """

    def __init__(self) -> None:
        # Maps channel name (e.g. "hospital", "donor", "emergency:EMR-2026-0001") -> set of active WebSockets
        self._channels: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str = "general") -> None:
        await websocket.accept()
        if channel not in self._channels:
            self._channels[channel] = set()
        self._channels[channel].add(websocket)
        logger.info("websocket_client_connected", channel=channel, active_clients=len(self._channels[channel]))

    def disconnect(self, websocket: WebSocket, channel: str = "general") -> None:
        if channel in self._channels:
            self._channels[channel].discard(websocket)
            if not self._channels[channel]:
                del self._channels[channel]
        logger.info("websocket_client_disconnected", channel=channel)

    async def broadcast(self, channel: str, message: Dict[str, Any]) -> None:
        """Broadcasts a JSON payload to all active clients connected to a specific channel."""
        if channel not in self._channels:
            return

        payload_str = json.dumps(message)
        dead_connections: List[WebSocket] = []

        for connection in list(self._channels[channel]):
            try:
                await connection.send_text(payload_str)
            except Exception as e:
                logger.warning("websocket_send_failed", channel=channel, error=str(e))
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead, channel)

    async def broadcast_all(self, message: Dict[str, Any]) -> None:
        """Broadcasts a high-priority system-wide event across all registered channels."""
        payload_str = json.dumps(message)
        for channel, sockets in list(self._channels.items()):
            dead_connections: List[WebSocket] = []
            for connection in list(sockets):
                try:
                    await connection.send_text(payload_str)
                except Exception as e:
                    logger.warning("websocket_broadcast_all_failed", channel=channel, error=str(e))
                    dead_connections.append(connection)

            for dead in dead_connections:
                self.disconnect(dead, channel)


# Singleton manager instance
ws_manager = WebSocketConnectionManager()
