from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Literal
from pydantic.alias_generators import to_camel


class BetType(str, Enum):
    SPREAD_HOME = "SPREAD_HOME"
    SPREAD_AWAY = "SPREAD_AWAY"
    MONEYLINE_HOME = "MONEYLINE_HOME"
    MONEYLINE_AWAY = "MONEYLINE_AWAY"
    OVER = "OVER"
    UNDER = "UNDER"


class UserBetWithGameInfo(BaseModel):
    id: int
    user_id: int
    # API game id, not db game id
    game_id: Optional[str]
    bet_type: BetType
    odds: Decimal
    amount_placed: Decimal
    total_payout: Decimal
    placed_at: datetime
    status: str
    betting_line: Optional[Decimal]

    # Extra fields from Game
    home_team: str
    away_team: str
    game_date: datetime

    class Config:
        from_attributes = True
        alias_generator = to_camel
        populate_by_name = True


class PlaceBetRequest(BaseModel):
    game_id: Optional[str] = Field(None, alias="gameId")
    bet_type: BetType = Field(alias="betType")
    amount_to_place: Decimal = Field(alias="amountToPlace")
    odds: Decimal
    betting_line: Optional[Decimal] = Field(None, alias="bettingLine")
    home_team: Optional[str] = Field(None, alias="homeTeam")
    away_team: Optional[str] = Field(None, alias="awayTeam")
    game_date: Optional[str] = Field(None, alias="gameDate")

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "gameId": "0112102",
                "betType": "SPREAD_HOME",
                "amountToPlace": 100.00,
                "odds": -110,
                "bettingLine": 12.5,
                "homeTeam": "Orlando Magic",
                "awayTeam": "Atlanta Hawks",
                "game_date": "2025-04-15",
            }
        }


class BetResponse(BaseModel):
    id: int
    user_id: int = Field(alias="userId")
    game_id: int = Field(alias="gameId")
    bet_type: BetType = Field(alias="betType")
    odds: Decimal
    amount_placed: Decimal = Field(alias="amountPlaced")
    total_payout: Decimal = Field(alias="totalPayout")
    placed_at: datetime = Field(alias="placedAt")
    status: str

    class Config:
        alias_generator = to_camel
        from_attributes = True
        populate_by_name = True


class Period(BaseModel):
    period: int
    periodType: str
    score: int


class PlayerStatistics(BaseModel):
    assists: int
    blocks: int
    blocksReceived: int
    fieldGoalsAttempted: int
    fieldGoalsMade: int
    fieldGoalsPercentage: float
    foulsOffensive: int
    foulsDrawn: int
    foulsPersonal: int
    foulsTechnical: int
    freeThrowsAttempted: int
    freeThrowsMade: int
    freeThrowsPercentage: float
    minus: int
    minutes: str
    minutesCalculated: str
    plus: int
    plusMinusPoints: int
    points: int
    pointsFastBreak: int
    pointsInThePaint: int
    pointsSecondChance: int
    reboundsDefensive: int
    reboundsOffensive: int
    reboundsTotal: int
    steals: int
    threePointersAttempted: int
    threePointersMade: int
    threePointersPercentage: float
    turnovers: int
    twoPointersAttempted: int
    twoPointersMade: int
    twoPointersPercentage: float


class Player(BaseModel):
    status: Literal["ACTIVE", "INACTIVE"]
    order: int
    personId: int
    jerseyNum: str
    position: Optional[str] = None
    starter: str
    oncourt: str
    played: str
    statistics: PlayerStatistics
    name: str
    nameI: str
    firstName: str
    familyName: str
    notPlayingReason: Optional[str] = None
    notPlayingDescription: Optional[str] = None


class TeamStatistics(BaseModel):
    assists: int
    assistsTurnoverRatio: float
    benchPoints: int
    biggestLead: int
    biggestLeadScore: str
    biggestScoringRun: int
    biggestScoringRunScore: str
    blocks: int
    blocksReceived: int
    fastBreakPointsAttempted: int
    fastBreakPointsMade: int
    fastBreakPointsPercentage: float
    fieldGoalsAttempted: int
    fieldGoalsEffectiveAdjusted: float
    fieldGoalsMade: int
    fieldGoalsPercentage: float
    foulsOffensive: int
    foulsDrawn: int
    foulsPersonal: int
    foulsTeam: int
    foulsTechnical: int
    foulsTeamTechnical: int
    freeThrowsAttempted: int
    freeThrowsMade: int
    freeThrowsPercentage: float
    leadChanges: int
    minutes: str
    minutesCalculated: str
    points: int
    pointsAgainst: int
    pointsFastBreak: int
    pointsFromTurnovers: int
    pointsInThePaint: int
    pointsInThePaintAttempted: int
    pointsInThePaintMade: int
    pointsInThePaintPercentage: float
    pointsSecondChance: int
    reboundsDefensive: int
    reboundsOffensive: int
    reboundsPersonal: int
    reboundsTeam: int
    reboundsTeamDefensive: int
    reboundsTeamOffensive: int
    reboundsTotal: int
    secondChancePointsAttempted: int
    secondChancePointsMade: int
    secondChancePointsPercentage: float
    steals: int
    threePointersAttempted: int
    threePointersMade: int
    threePointersPercentage: float
    timeLeading: str
    timesTied: int
    trueShootingAttempts: float
    trueShootingPercentage: float
    turnovers: int
    turnoversTeam: int
    turnoversTotal: int
    twoPointersAttempted: int
    twoPointersMade: int
    twoPointersPercentage: float


class Team(BaseModel):
    teamId: int
    teamName: str
    teamCity: str
    teamTricode: str
    teamSlug: str
    wins: int
    losses: int
    score: int
    seed: int
    inBonus: None = None
    timeoutsRemaining: int
    periods: List[Period]
    players: List[Player]
    statistics: TeamStatistics
