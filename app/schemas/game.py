from pydantic import BaseModel, Field, RootModel
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, List
from pydantic.alias_generators import to_camel


class GameResponse(BaseModel):
    id: int
    game_id: Optional[str] = Field(alias="gameId")
    home_team: str = Field(alias="homeTeam")
    away_team: str = Field(alias="awayTeam")

    # spread fields
    home_spread_odds: Optional[Decimal] = Field(alias="homeSpreadOdds")
    away_spread_odds: Optional[Decimal] = Field(alias="awaySpreadOdds")
    home_spread: Optional[Decimal] = Field(alias="homeSpread")
    opening_home_spread: Decimal = Field(alias="openingHomeSpread")
    home_moneyline: Optional[Decimal] = Field(alias="homeMoneyline")
    away_moneyline: Optional[Decimal] = Field(alias="awayMoneyline")

    # over/under fields
    opening_over_under: Decimal = Field(alias="openingOverUnder")
    over_under: Optional[Decimal] = Field(alias="overUnder")
    over_odds: Optional[Decimal] = Field(alias="overOdds")
    under_odds: Optional[Decimal] = Field(alias="underOdds")

    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    game_date: date = Field(alias="gameDate")
    has_ended: bool = Field(alias="hasEnded")

    class Config:
        orm_mode = True
        from_attributes = True
        populate_by_name = True  # This allows population using the field names


class MarkGameEndedResponse(BaseModel):
    success: bool


class GameIdUpdateRequest(BaseModel):
    home_team: str
    away_team: str
    game_date: date
    game_id: str

    class Config:
        # Allow both snake_case and camelCase when creating objects
        alias_generator = to_camel
        populate_by_name = True
        # Example for API documentation
        json_schema_extra = {
            "example": {
                "homeTeam": "New York Knicks",
                "awayTeam": "Brooklyn Nets",
                "gameDate": "2025-01-11",
                "gameId": "0112102",
            }
        }


class ProcessResponse(BaseModel):
    success: bool
    message: str
    game_id: str


class ProcessResponse(BaseModel):
    success: bool
    message: str
    game_id: str


class CurrentGameBettingInfos(RootModel):
    root: Dict[str, List[GameResponse]]

    model_config = {"populate_by_name": True, "alias_generator": to_camel}

    def __init__(self, **data):
        super().__init__(**data)
        if not self.root:
            raise ValueError("At least one date key must exist")

    @property
    def dates(self) -> List[str]:
        return list(self.root.keys())
