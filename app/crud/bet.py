from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
from app.models.bet import Bet
from app.models.game import Game
from app.models.user import User
from app.schemas.bet import PlaceBetRequest
from fastapi import HTTPException

class BetCRUD:
    @staticmethod
    def get_user_bets(db: Session, user_id: int) -> list[Bet]:
        return db.query(Bet)\
            .filter(Bet.user_id == user_id)\
            .order_by(Bet.placed_at.desc())\
            .all()

    @staticmethod
    def create_bet(db: Session, user_id: int, request: PlaceBetRequest) -> Bet:
        # Fetch game
        game = db.query(Game).filter(Game.game_id == request.game_id).first()
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")

        # Create bet
        bet = Bet(
            user_id=user_id,
            game_id=request.game_id,
            bet_type=request.bet_type,
            amount_placed=request.amount_to_place,
            odds=request.odds,
            status="PENDING"
        )

        # Calculate odds and payout
        BetCRUD._calculate_odds_and_payout(bet)

        # Update user statistics
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.amount_placed = (user.amount_placed or 0) + float(request.amount_to_place)
            user.bets_placed = (user.bets_placed or 0) + 1

        # db.add(bet)
        # db.commit()
        # db.refresh(bet)
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
        total_payout = total_payout.quantize(Decimal('.01'))

        bet.total_payout = total_payout