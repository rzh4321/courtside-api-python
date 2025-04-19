from pydantic import BaseModel
from app.models.user import User
from datetime import datetime


class DepositRequest(BaseModel):
    amount: float


class DepositResponse(BaseModel):
    success: bool
