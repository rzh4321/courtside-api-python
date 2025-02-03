from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone
from typing import List, Optional
from app.models.game import Game
import logging

logger = logging.getLogger(__name__)

class GameCRUD:
    @staticmethod
    def get_all(db: Session) -> List[Game]:
        res =  db.query(Game).all()
        return res

    @staticmethod
    def get_by_date(db: Session, date: datetime) -> List[Game]:
        return db.query(Game).filter(Game.game_date == date).all()

    @staticmethod
    def get_by_game_id(db: Session, game_id: str) -> Optional[Game]:
        return db.query(Game).filter(Game.game_id == game_id).first()

    @staticmethod
    def get_by_teams_and_date(
        db: Session, 
        home_team: str, 
        away_team: str, 
        game_date: datetime
    ) -> Optional[Game]:
        logger.info(f"Finding game: {home_team} AT {away_team} ON {game_date}")
        return db.query(Game).filter(
            and_(
                Game.home_team == home_team,
                Game.away_team == away_team,
                Game.game_date == game_date
            )
        ).first()

    @staticmethod
    def update_game_id(
        db: Session,
        home_team: str,
        away_team: str,
        game_date: datetime,
        game_id: str
    ) -> Optional[Game]:
        game = GameCRUD.get_by_teams_and_date(db, home_team, away_team, game_date)
        if game:
            game.game_id = game_id
        return game