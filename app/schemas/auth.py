from pydantic import BaseModel
from app.models.user import User
from datetime import datetime


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
    amount_deposited: float
    amount_placed: float
    amount_won: float
    bets_placed: int
    bets_won: int
    balance: float

    class Config:
        # need this to validate User sqlalchemy object
        from_attributes = True


class AuthResponse(BaseModel):
    token: str
    user: UserResponse


class TokenData(BaseModel):
    username: str | None = None


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str
