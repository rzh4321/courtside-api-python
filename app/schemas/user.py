from pydantic import BaseModel
from app.models.user import User
from datetime import datetime
from .bet import BetResponse
from typing import List

class DepositRequest(BaseModel):
    amount: float


class DepositResponse(BaseModel):
    success: bool


class BetsResponse(BaseModel):
    bets: List[BetResponse]