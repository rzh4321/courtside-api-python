from fastapi import WebSocket
from typing import Set, Dict, Any
import json
from app.schemas.game import GameResponse
from datetime import date, datetime
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        return super(DecimalEncoder, self).default(obj)

class OddsWebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"Client connected. Total connections: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast_odds_update(self, game_id: str, game_data: dict):
        payload = {
            "type": "ODDS_UPDATE",
            "gameId": game_id,
            "data": game_data
        }
        await self._broadcast_message(payload)

    async def broadcast_odds_update_by_teams(self, home_team: str, away_team: str, game_date: str, game_data: GameResponse):
        payload = {
            "type": "ODDS_UPDATE_BY_TEAMS",
            "homeTeam": home_team,
            "awayTeam": away_team,
            "gameDate": game_date,
            "data": game_data
        }
        await self._broadcast_message(payload)

    async def _broadcast_message(self, payload: Dict[str, Any]):
        dead_connections = set()
        json_str = json.dumps(payload, cls=DecimalEncoder)
        
        for connection in self.active_connections:
            try:
                await connection.send_text(json_str)  # Use send_text instead of send_json
            except Exception as e:
                print(f"Error sending message: {e}")
                dead_connections.add(connection)
        
        # Remove dead connections
        for dead_connection in dead_connections:
            self.active_connections.remove(dead_connection)