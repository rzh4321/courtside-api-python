from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.db.base import Base
from app.db.session import engine
from app.api.v1.endpoints import games, auth, bets, websocket, odds
import logging
from fastapi.middleware.cors import CORSMiddleware


# uvicorn app.main:app --reload
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://nba-courtside.vercel.app",
    "http://52.15.214.190",
    "https://52.15.214.190"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    allow_websockets=True
)

# Include routers
app.include_router(games.router, prefix="/api/games", tags=["games"])
app.include_router(bets.router, prefix="/api/bets", tags=["bets"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(odds.router, prefix="/api", tags=["odds"])

app.include_router(websocket.router)


# test endpoint to verify database connection
@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        # Execute a simple query
        db.execute(text("SELECT 1"))
        return {"message": "Database connection successful!"}
    except Exception as e:
        return {"error": str(e)}