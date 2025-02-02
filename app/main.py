from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.db.base import Base
from app.db.session import engine
from app.api.v1.endpoints import games
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NBA Courtside")

# Include routers
app.include_router(games.router, prefix="/api/games", tags=["games"])

# test endpoint to verify database connection
@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        # Execute a simple query
        db.execute(text("SELECT 1"))
        return {"message": "Database connection successful!"}
    except Exception as e:
        return {"error": str(e)}