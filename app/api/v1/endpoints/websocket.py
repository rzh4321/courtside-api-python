from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets.odds_manager import OddsWebSocketManager

router = APIRouter()
odds_manager = OddsWebSocketManager()

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://nba-courtside.vercel.app",
    "http://52.15.214.190",
    "https://52.15.214.190"
]

@router.websocket("/ws/odds")
async def websocket_endpoint(websocket: WebSocket):
    try:
        client_origin = websocket.headers.get("origin")
        print(f"Incoming WebSocket connection from origin: {client_origin}")
        
        if client_origin not in ALLOWED_ORIGINS:
            print(f"Rejected connection from unauthorized origin: {client_origin}")
            await websocket.close(code=1008, reason="Not allowed")
            return
            
        await odds_manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
        except WebSocketDisconnect:
            await odds_manager.disconnect(websocket)
    except Exception as e:
        print(f"Error in websocket endpoint: {str(e)}")
        if not websocket.client_state.disconnected:
            await websocket.close(code=1011, reason=str(e))