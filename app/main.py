from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.db.base import Base
from app.db.session import engine
from app.api.v1.endpoints import games, auth, bets
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Include routers
app.include_router(games.router, prefix="/api/games", tags=["games"])
app.include_router(bets.router, prefix="/api/bets", tags=["bets"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])


# test endpoint to verify database connection
@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        # Execute a simple query
        db.execute(text("SELECT 1"))
        return {"message": "Database connection successful!"}
    except Exception as e:
        return {"error": str(e)}