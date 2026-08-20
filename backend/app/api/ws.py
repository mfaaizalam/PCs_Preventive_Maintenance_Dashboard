from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.ws_manager import manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/dashboard")
async def dashboard_ws(websocket: WebSocket):
    """
    Dashboard browsers connect here. This is a one-way push channel
    (server -> browser) - we don't expect meaningful data back. We
    still block on receive_text() so we notice a closed connection
    promptly, and so the browser can send a lightweight "ping" to
    keep some reverse proxies from timing out an idle socket.
    """
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception:
        await manager.disconnect(websocket)