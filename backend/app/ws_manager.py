"""
In-memory WebSocket connection manager for pushing live updates to the
dashboard.

IMPORTANT - single-process assumption:
This keeps connected sockets in a plain Python set living inside ONE
running uvicorn process. That's fine for one backend process on one
server PC (your deployment). Don't run `uvicorn --workers 2+`, and
don't run two independent backend processes behind a load balancer,
unless you also add a shared broker (e.g. Redis pub/sub) so every
process knows about every connected browser.
"""

import asyncio
import json
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger("app.ws")


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)
        logger.info("WS client connected (total=%d)", len(self._connections))

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)
        logger.info("WS client disconnected (total=%d)", len(self._connections))

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Send a JSON message to every connected dashboard. A socket
        that fails to receive it (closed tab, network blip, etc.) is
        dropped instead of breaking the whole broadcast."""
        if not self._connections:
            return

        payload = json.dumps(message)

        async with self._lock:
            targets = list(self._connections)

        dead: list[WebSocket] = []
        for ws in targets:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)

        if dead:
            async with self._lock:
                for ws in dead:
                    self._connections.discard(ws)


# Single shared instance - import this from anywhere that needs to
# broadcast (e.g. app/api/agent.py after a report is saved).
manager = ConnectionManager()