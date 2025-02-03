from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.crud.user import authenticate_user, create_user
from app.db.session import get_db
from app.schemas.auth import AuthResponse, UserCreate, UserLogin

router = APIRouter()

@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, credentials.username, credentials.password)
    print(f'user is {user}')
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    print(f'access token is {type(access_token)}')
    return {"access_token": access_token, "user": user}

@router.post("/register", response_model=AuthResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    user, access_token = create_user(db, user_data.username, user_data.password)
    return {"access_token": access_token, "user": user}