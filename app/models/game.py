from sqlalchemy import Column, BigInteger, String, Numeric, DateTime, Date, func, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.db.base import Base
from app.models.bet import Bet


class Game(Base):
    __tablename__ = 'games'

    id = Column(BigInteger, primary_key=True)
    
    # game information
    game_id = Column(String(255), unique=True, index=True)
    home_team = Column(String(255), nullable=False)
    away_team = Column(String(255), nullable=False)
    
    # spread
    home_spread_odds = Column(Numeric(6, 2))
    away_spread_odds = Column(Numeric(6, 2))
    home_spread = Column(Numeric(5, 2))
    opening_home_spread = Column(Numeric(5, 2), nullable=False)
    home_moneyline = Column(Numeric(8, 2))
    away_moneyline = Column(Numeric(8, 2))
    
    # over/under
    opening_over_under = Column(Numeric(5, 2), nullable=False)
    over_under = Column(Numeric(5, 2))
    over_odds = Column(Numeric(6, 2))
    under_odds = Column(Numeric(6, 2))
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    game_date = Column(Date, nullable=False)
    has_ended = Column(Boolean, nullable=False, default=False)

    bets = relationship("Bet", back_populates="game", lazy="dynamic")

    def __repr__(self):
        return (
            f"<Game("
            f"game_id={self.game_id}, "
            f"home_team={self.home_team}, "
            f"away_team={self.away_team}, "
            f"game_date={self.game_date}"
            f"has_ended={self.has_ended}"
            f")>"
        )