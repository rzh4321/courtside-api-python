from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic.alias_generators import to_camel

class BetType(str, Enum):
    SPREAD_HOME = "SPREAD_HOME"
    SPREAD_AWAY = "SPREAD_AWAY"
    MONEYLINE_HOME = "MONEYLINE_HOME"
    MONEYLINE_AWAY = "MONEYLINE_AWAY"
    OVER = "OVER"
    UNDER = "UNDER"

class PlaceBetRequest(BaseModel):
    game_id: str = Field(alias="gameId")
    bet_type: BetType = Field(alias="betType")
    amount_to_place: Decimal = Field(alias="amountToPlace")
    odds: Decimal

    class Config:
        alias_generator= to_camel
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "gameId": "0112102",
                "betType": "SPREAD_HOME",
                "amountToPlace": 100.00,
                "odds": -110
            }
        }

class BetResponse(BaseModel):
    id: int
    user_id: int = Field(alias="userId")
    game_id: str = Field(alias="gameId")
    bet_type: BetType = Field(alias="betType")
    odds: Decimal
    amount_placed: Decimal = Field(alias="amountPlaced")
    total_payout: Decimal = Field(alias="totalPayout")
    placed_at: datetime = Field(alias="placedAt")
    status: str
    home_team: str = Field(alias="homeTeam")
    away_team: str = Field(alias="awayTeam")

    class Config:
        alias_generator= to_camel
        from_attributes = True
        populate_by_name = True