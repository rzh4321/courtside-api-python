from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud.user import UserCRUD
from app.core.auth import get_current_user
from app.db.session import get_db
from app.schemas.user import DepositRequest, DepositResponse, UserResponse
from app.models.user import User

router = APIRouter()


@router.post("/deposit", response_model=DepositResponse)
def deposit(
    request: DepositRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"success": UserCRUD.deposit(db, current_user.username, request.amount)}


@router.get("/", response_model=UserResponse)
def get_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = UserCRUD.get_user_by_username(db, current_user.username)
    return user
