from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from app.models.game import Game
from app.models.bet import Bet
from app.crud.bet import BetCRUD
from app.schemas.game import CurrentGameBettingInfos, GameResponse
import logging
import aiohttp
import pytz

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
    def mark_game_ended(db: Session, game_id: str) -> bool:
        game = GameCRUD.get_by_game_id(game_id)
        if game:
            game.has_ended = True
            return True
        return False

    @staticmethod
    async def get_boxscore(game_id: str):
        """Fetch boxscore data from NBA API"""
        host = "https://cdn.nba.com"
        url = f"{host}/static/json/liveData/boxscore/boxscore_{game_id}.json"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
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

    @staticmethod
    def get_todays_odds(db: Session) -> CurrentGameBettingInfos:
        logger.info("IN TODAY ENDPOINT")

        eastern = pytz.timezone("US/Eastern")
        today_est = datetime.now(eastern)
        # Subtract 2 hours (if its 1:45 AM April 20, it becomes 11:45 PM April 19)
        # This is for getting "yesterdays" games that are ongoing when it's like 12:30 AM
        adjusted_time = today_est - timedelta(hours=2)
        yesterday_time = adjusted_time - timedelta(days=1)

        # Get the date from the adjusted time
        adjusted_date = adjusted_time.date()
        yesterday_date = yesterday_time.date()
        yesterday_str = yesterday_date.strftime("%Y-%m-%d")

        # Format the date as a string
        today_str = adjusted_date.strftime("%Y-%m-%d")
        print(f"Today is {today_str}")

        # Get the most recent date from the Game table
        most_recent_game = db.query(Game).order_by(desc(Game.game_date)).first()

        if not most_recent_game:
            # no games in the database (should never happen)
            return CurrentGameBettingInfos(root={"no_games": []})

        most_recent_date = most_recent_game.game_date.date()

        # Create response dictionary with dates as keys and game lists as values
        response_dict: Dict[str, List[GameResponse]] = {}

        # Get all games that haven't ended from the most recent date
        most_recent_date_games = (
            db.query(Game)
            .filter(and_(Game.game_date == most_recent_date, Game.has_ended == False))
            .all()
        )

        most_recent_date_str = most_recent_date.strftime("%Y-%m-%d")

        if most_recent_date_games:
            response_dict[
                most_recent_date_str if most_recent_date_str != today_str else "Today"
            ] = [GameResponse.model_validate(game) for game in most_recent_date_games]

        # Get all games from yesterday that haven't ended
        yesterdays_games = (
            db.query(Game)
            .filter(Game.game_date == yesterday_date, Game.has_ended == False)
            .all()
        )

        # Add yesterday's games if any exist
        if yesterdays_games:
            response_dict[yesterday_str] = [
                GameResponse.model_validate(game) for game in yesterdays_games
            ]

        # Ensure we have at least one date key
        if not response_dict:
            logger.info("No games found")
            # If no games found (eg. offseason), return an empty result
            return CurrentGameBettingInfos(root={"no_games": []})
        # print(response_dict)

        return CurrentGameBettingInfos(root=response_dict)
