from sqlalchemy.orm import Session
from sqlalchemy import and_
from decimal import Decimal
from datetime import datetime
from app.models.bet import Bet
from app.models.game import Game
from app.models.user import User
from app.schemas.bet import PlaceBetRequest, Team, UserBetWithGameInfo
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class BetCRUD:
    @staticmethod
    def get_user_bets(db: Session, user_id: int) -> list[UserBetWithGameInfo]:
        bets = (
            db.query(Bet)
            .filter(Bet.user_id == user_id)
            .order_by(Bet.placed_at.desc())
            .all()
        )
        result = []
        for bet in bets:
            game = db.query(Game).filter(Game.id == bet.game_id).first()
            if game:
                bet_with_game_info = {
                    "id": bet.id,
                    "user_id": bet.user_id,
                    "game_id": game.game_id,
                    "bet_type": bet.bet_type,
                    "odds": float(bet.odds),
                    "amount_placed": bet.amount_placed,
                    "total_payout": bet.total_payout,
                    "placed_at": bet.placed_at,
                    "status": bet.status,
                    "betting_line": bet.betting_line if bet.betting_line else None,
                    "home_team": game.home_team,
                    "away_team": game.away_team,
                    "game_date": game.game_date,
                }
                result.append(UserBetWithGameInfo.model_validate(bet_with_game_info))

        return result

    @staticmethod
    def create_bet(db: Session, user_id: int, request: PlaceBetRequest) -> Bet:
        # Fetch game from game_id, if given
        if request.game_id:
            game = db.query(Game).filter(Game.game_id == request.game_id).first()
        else:
            # game_id is not given, so team names and game date must be given
            date_obj = datetime.strptime(request.game_date, "%Y-%m-%d")
            game = (
                db.query(Game)
                .filter(
                    and_(
                        Game.home_team == request.home_team,
                        Game.away_team == request.away_team,
                        Game.game_date == date_obj,
                    )
                )
                .first()
            )
        user = db.query(User).filter(User.id == user_id).first()
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        if request.amount_to_place > user.balance:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        # Create bet
        bet = Bet(
            user_id=user_id,
            game_id=game.id,
            bet_type=request.bet_type,
            amount_placed=request.amount_to_place,
            odds=request.odds,
            status="PENDING",
            betting_line=request.betting_line,
        )

        # Calculate odds and payout
        BetCRUD._calculate_odds_and_payout(bet)
        # Update user statistics
        if user:
            user.amount_placed = (user.amount_placed or 0) + float(
                request.amount_to_place
            )
            user.bets_placed = (user.bets_placed or 0) + 1
            user.balance = user.balance - request.amount_to_place
        # need these to automatically populate the id and placed_at columns
        db.add(bet)
        db.commit()
        db.refresh(bet)
        return bet

    @staticmethod
    def process_bet(db: Session, bet: Bet, home_team: Team, away_team: Team) -> Bet:
        logger.info(f"\nPROCESSING BET {bet}")
        away_team_name = away_team["teamCity"] + away_team["teamName"]
        home_team_name = home_team["teamCity"] + home_team["teamName"]
        away_team_score = away_team["score"]
        home_team_score = home_team["score"]
        total_score = away_team_score + home_team_score

        logger.info(
            f"THE GAME IS {away_team_name} AT {home_team_name}, {away_team_score} - {home_team_score}. TOTAL IS {total_score}"
        )
        user = db.query(User).filter(User.id == bet.user_id).first()
        logger.info(f"THIS WAS PLACED BY USER {user}")

        bet_won = False
        push = False

        if bet.bet_type == "SPREAD_HOME":
            logger.info(f"IT BET ON SPREAD HOME, {home_team_name} {bet.betting_line}")

            if (
                bet.betting_line > 0
                and home_team_score + bet.betting_line > away_team_score
            ) or (
                bet.betting_line < 0
                and home_team_score - away_team_score >= abs(bet.betting_line)
            ):
                logger.info("HOME TEAM COVERED SPREAD")
                bet_won = True

        elif bet.bet_type == "SPREAD_AWAY":
            logger.info(f"IT BET ON SPREAD AWAY, {away_team_name} {bet.betting_line}")

            if (
                bet.betting_line > 0
                and away_team_score + bet.betting_line > home_team_score
            ) or (
                bet.betting_line < 0
                and away_team_score - home_team_score >= abs(bet.betting_line)
            ):
                logger.info("AWAY TEAM COVERED SPREAD")
                bet_won = True

        elif bet.bet_type == "OVER":
            logger.info(f"IT BET ON OVER {bet.betting_line}")

            if total_score > bet.betting_line:
                logger.info(f"OVER HIT: {total_score} > {bet.betting_line}")
                bet_won = True
            elif total_score == bet.betting_line:
                logger.info(f"SCORE EQUALS LINE. PUSH")
                push = True

        elif bet.bet_type == "UNDER":
            logger.info(f"IT BET ON UNDER {bet.betting_line}")

            if total_score < bet.betting_line:
                logger.info(f"UNDER HIT: {total_score} < {bet.betting_line}")
                bet_won = True
            elif total_score == bet.betting_line:
                logger.info(f"SCORE EQUALS LINE. PUSH")
                push = True

        elif bet.bet_type == "MONEYLINE_HOME":
            logger.info(f"IT BET ON MONEYLINE HOME, {home_team_name}")

            if home_team_score > away_team_score:
                logger.info(f"HOME TEAM WON STRAIGHT UP")
                bet_won = True

        elif bet.bet_type == "MONEYLINE_AWAY":
            logger.info(f"IT BET ON MONEYLINE AWAY, {away_team_name}")

            if away_team_score > home_team_score:
                logger.info(f"AWAY TEAM WON STRAIGHT UP")
                bet_won = True

        # Process winning bet
        if bet_won:
            user.amount_won += bet.total_payout
            user.bets_won += 1
            user.balance += bet.total_payout
            bet.status = "WON"
            logger.info(f"BET WON: User {user.id} won {bet.total_payout}")
            # TODO: send websocket message to react to update user context stats
        elif push:
            bet.status = "PUSH"
            logger.info(f"BET IS A PUSH: {bet.bet_type}")
            user.balance += bet.amount_placed
        else:
            bet.status = "LOST"
            logger.info(f"BET LOST: {bet.bet_type}")

        return bet

    @staticmethod
    def _calculate_odds_and_payout(bet: Bet):
        amount_placed = Decimal(str(bet.amount_placed))
        odds = Decimal(str(bet.odds))

        # Convert American odds to decimal odds
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1

        # Calculate total payout
        total_payout = amount_placed * Decimal(str(decimal_odds))
        total_payout = total_payout.quantize(Decimal(".01"))

        bet.total_payout = total_payout
