from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timezone, timedelta
from app.db.session import get_db
from app.crud.game import GameCRUD
from app.schemas.game import (
    GameResponse,
    GameIdUpdateRequest,
    ProcessResponse,
    CurrentGameBettingInfos,
    GameResponse,
    MarkGameEndedResponse,
)
import logging
from app.models.game import Game
import pytz


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=List[GameResponse])
def get_all_games(db: Session = Depends(get_db)):
    games = GameCRUD.get_all(db)
    return games


@router.get("/date/{date}", response_model=List[GameResponse])
def get_games_by_date(date: str, db: Session = Depends(get_db)):
    try:
        # Parse date string to datetime
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        # Set to start of day in EST
        date_obj = date_obj.replace(tzinfo=timezone.utc)
        return GameCRUD.get_by_date(db, date_obj)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")


@router.get(
    "/by-teams/{home_team}/{away_team}/{game_date}", response_model=GameResponse
)
def get_game_by_teams(
    home_team: str, away_team: str, game_date: str, db: Session = Depends(get_db)
):
    try:
        logger.info(f"IN FIND BY TEAMS. {home_team} AT {away_team} ON {game_date}")
        date_obj = datetime.strptime(game_date, "%Y-%m-%d")

        game = GameCRUD.get_by_teams_and_date(db, home_team, away_team, date_obj)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        return game
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")


@router.put("/set-game-id", response_model=GameResponse)
def set_game_id(request: GameIdUpdateRequest, db: Session = Depends(get_db)):
    try:
        game = GameCRUD.update_game_id(
            db, request.home_team, request.away_team, request.game_date, request.game_id
        )
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        return game
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")


@router.put("/mark-game-ended/{game_id}", response_model=MarkGameEndedResponse)
def mark_game_ended(game_id: str, db: Session = Depends(get_db)):
    success = GameCRUD.mark_game_ended(db, game_id)
    if not success:
        raise HTTPException(status_code=404, detail="Game not found")
    return {"success": True}


@router.post("/{game_id}/process", response_model=ProcessResponse)
async def process_game(game_id: str, db: Session = Depends(get_db)):
    logger.info(f"IN PROCESS GAME. GAME ID IS {game_id}")
    try:
        game = await GameCRUD.process_game(db, game_id)
        if game is None:
            raise HTTPException(
                status_code=404, detail="Game not found or game did not end"
            )

        return {
            "success": True,
            "message": "Game processed successfully",
            "game_id": game_id,
        }
    except Exception as e:
        logger.error(f"Error processing game {game_id}: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to process game: {str(e)}",
            "game_id": game_id,
        }


@router.get("/today", response_model=CurrentGameBettingInfos)
def get_todays_odds(db: Session = Depends(get_db)):
    betting_infos = GameCRUD.get_todays_odds(db)
    print(betting_infos)
    print(f"\n\n")
    if not betting_infos:
        raise HTTPException(status_code=500, detail="Return object was None")
    return betting_infos


@router.get("/{game_id}", response_model=GameResponse)
def get_game_by_id(game_id: str, db: Session = Depends(get_db)):
    game = GameCRUD.get_by_game_id(db, game_id)
    if not game:
        raise HTTPException(
            status_code=404, detail=f"Game not found with id: {game_id}"
        )
    return game
