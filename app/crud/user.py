from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash, verify_password
from typing import Optional
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from fastapi import HTTPException
from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    print(f'in authenticate user')
    user = get_user_by_username(db, username)
    if not user:
        print('couldnt find user')
        return None
    if not verify_password(password, user.password):
        print('wrong pw')
        return None
    return user

def create_user(db: Session, username: str, password: str) -> tuple[User, str]:
    try:
        # Check if user exists
        existing_user = get_user_by_username(db, username)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already registered"
            )

        # Create new user
        hashed_password = get_password_hash(password)
        db_user = User(username=username, password=hashed_password)
        # db.add(db_user)
        # db.commit()
        # db.refresh(db_user)

        # Generate token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.username},
            expires_delta=access_token_expires
        )

        return db_user, access_token

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )