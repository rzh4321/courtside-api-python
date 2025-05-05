from pydantic import BaseModel
from app.models.user import User
from datetime import datetime
from .bet import BetResponse
from typing import List
from decimal import Decimal
from pydantic.alias_generators import to_camel


class DepositRequest(BaseModel):
    amount: float


class DepositResponse(BaseModel):
    success: bool


class BetsResponse(BaseModel):
    bets: List[BetResponse]


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
    amount_deposited: Decimal
    balance: Decimal
    amount_placed: Decimal
    amount_won: Decimal
    bets_placed: int
    bets_won: int

    class Config:
        from_attributes = True
        alias_generator = to_camel
        populate_by_name = True
