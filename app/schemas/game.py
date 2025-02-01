from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

class GameResponse(BaseModel):
    id: int
    game_id: str
    home_team: str
    away_team: str
    
    # spread fields
    home_spread_odds: Optional[Decimal]
    away_spread_odds: Optional[Decimal]
    home_spread: Optional[Decimal]
    opening_home_spread: Decimal
    home_moneyline: Optional[Decimal]
    away_moneyline: Optional[Decimal]
    
    # over/under fields
    opening_over_under: Decimal
    over_under: Optional[Decimal]
    over_odds: Optional[Decimal]
    under_odds: Optional[Decimal]
    
    created_at: datetime
    updated_at: datetime
    game_date: date
    has_ended: bool

    class Config:
        orm_mode = True  # Allows Pydantic to read data from ORM objects
        # convert to camel case
        alias_generator = lambda string: ''.join(
            word if i == 0 else word.capitalize()
            for i, word in enumerate(string.split('_'))
        )

class GameIdUpdateRequest(BaseModel):
    home_team: str
    away_team: str
    game_date: date
    game_id: str

    class Config:
        # Convert snake_case to camelCase
        alias_generator = lambda string: ''.join(
            word if i == 0 else word.capitalize()
            for i, word in enumerate(string.split('_'))
        )
        # Allow both snake_case and camelCase when creating objects
        populate_by_name = True
        # Example for API documentation
        json_schema_extra = {
            "example": {
                "homeTeam": "New York Knicks",
                "awayTeam": "Brooklyn Nets",
                "gameDate": "2025-01-11",
                "gameId": "0112102"
            }
        }
