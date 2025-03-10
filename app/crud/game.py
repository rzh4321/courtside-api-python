from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone
from typing import List, Optional
from app.models.game import Game
from app.models.bet import Bet
from app.crud.bet import BetCRUD
import logging
import aiohttp
import ssl

logger = logging.getLogger(__name__)


class GameCRUD:
    @staticmethod
    def get_all(db: Session) -> List[Game]:
        res = db.query(Game).all()
        return res

    @staticmethod
    def get_by_date(db: Session, date: datetime) -> List[Game]:
        return db.query(Game).filter(Game.game_date == date).all()

    @staticmethod
    def get_by_game_id(db: Session, game_id: str) -> Optional[Game]:
        return db.query(Game).filter(Game.game_id == game_id).first()

    @staticmethod
    def get_by_teams_and_date(
        db: Session, home_team: str, away_team: str, game_date: datetime
    ) -> Optional[Game]:
        print(f"Finding game: {home_team} AT {away_team} ON {game_date}")
        return (
            db.query(Game)
            .filter(
                and_(
                    Game.home_team == home_team,
                    Game.away_team == away_team,
                    Game.game_date == game_date,
                )
            )
            .first()
        )

    @staticmethod
    def update_game_id(
        db: Session, home_team: str, away_team: str, game_date: datetime, game_id: str
    ) -> Optional[Game]:
        game = GameCRUD.get_by_teams_and_date(db, home_team, away_team, game_date)
        if game:
            game.game_id = game_id
        return game

    @staticmethod
    async def get_boxscore(game_id: str):
        """Fetch boxscore data from NBA API"""
        host = "https://cdn.nba.com"
        url = f"{host}/static/json/liveData/boxscore/boxscore_{game_id}.json"

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=ssl_context) as response:
                if response.status != 200:
                    logger.error(
                        f"Failed to fetch boxscore for game_id {game_id}: Status {response.status}"
                    )
                    return None
                data = await response.json()
                return data["game"]

    @staticmethod
    async def process_game(db: Session, game_id: str) -> Optional[Game]:
        game = db.query(Game).filter(Game.game_id == game_id).first()
        logger.info(f"\nPROCESSING GAME {game}")
        if game:
            boxscore_data = await GameCRUD.get_boxscore(game.game_id)
            if not boxscore_data:
                logger.error(
                    f"Could not process game {game_id}: Failed to fetch boxscore data"
                )
                raise Exception("Game has not ended")

            home_team_stats = boxscore_data["homeTeam"]
            away_team_stats = boxscore_data["awayTeam"]
            logger.info(
                f"GAME STATUS IS {boxscore_data['gameStatus']} (IT SHOULD BE 3)"
            )
            if boxscore_data["gameStatus"] != 3:
                logger.error(
                    f"GAMAE STATUS IS NOT 3 SO IT HASNT ENDED, MUST BE PROB WITH SCRAPER. RETURNING"
                )
                return None
            bets = (
                db.query(Bet)
                .filter(and_(Bet.game_id == game.id, Bet.status == "PENDING"))
                .all()
            )
            logger.info(f"FOUND BETS: {len(bets)}")
            for bet in bets:
                BetCRUD.process_bet(db, bet, home_team_stats, away_team_stats)
        return game
