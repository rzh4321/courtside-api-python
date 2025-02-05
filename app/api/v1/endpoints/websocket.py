from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets.odds_manager import OddsWebSocketManager

router = APIRouter()
odds_manager = OddsWebSocketManager()

@router.websocket("/ws/odds")
async def websocket_endpoint(websocket: WebSocket):
    await odds_manager.connect(websocket)
    try:
        while True:
            # Wait for messages if needed
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        await odds_manager.disconnect(websocket)