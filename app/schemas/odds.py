from pydantic import BaseModel, Field
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from pydantic.alias_generators import to_camel

class UpdateOddsRequest(BaseModel):
    game_id: str = Field(alias="gameId")

    class Config:
        populate_by_name = True  # This allows population using the field names

class UpdateOddsByTeamsRequest(BaseModel):
    home_team: str
    away_team: str
    game_date: str

    class Config:
        alias_generator= to_camel
        populate_by_name = True