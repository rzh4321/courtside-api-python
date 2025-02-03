from enum import Enum
from sqlalchemy import Column, BigInteger, String, Numeric, DateTime, func, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from app.models.user import User


class BetType(str, Enum):
    SPREAD_HOME = "SPREAD_HOME"
    SPREAD_AWAY = "SPREAD_AWAY"
    MONEYLINE_HOME = "MONEYLINE_HOME"
    MONEYLINE_AWAY = "MONEYLINE_AWAY"
    OVER = "OVER"
    UNDER = "UNDER"


class Bet(Base):
    __tablename__ = 'bets'

    id = Column(BigInteger, primary_key=True)
    
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    game_id = Column(BigInteger, ForeignKey('games.id'), nullable=False)
    
    user = relationship("User", back_populates="bets")
    game = relationship("Game", back_populates="bets")
    
    bet_type = Column(SQLEnum(BetType), nullable=False)
    odds = Column(Numeric(6, 2), nullable=False)
    amount_placed = Column(Numeric(10, 2), nullable=False)
    total_payout = Column(Numeric(10, 2), nullable=False)
    
    placed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    status = Column(
        String(20),
        default="PENDING",
        nullable=False
    )

    def __repr__(self):
        return (
            f"<Bet("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"game_id={self.game_id}, "
            f"bet_type={self.bet_type}, "
            f"status={self.status}"
            f")>"
        )