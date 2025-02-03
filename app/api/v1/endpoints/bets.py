from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.bet import BetResponse, PlaceBetRequest
from app.crud.bet import BetCRUD
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("", response_model=List[BetResponse])
def get_current_user_bets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return BetCRUD.get_user_bets(db, current_user.id)

@router.post("", response_model=BetResponse)
def place_bet(
    request: PlaceBetRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return BetCRUD.create_bet(db, current_user.id, request)