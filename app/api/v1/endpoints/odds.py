from app.api.v1.endpoints.websocket import odds_manager
from sqlalchemy.orm import Session
from app.schemas.odds import UpdateOddsRequest, UpdateOddsByTeamsRequest
from app.schemas.game import GameResponse
from fastapi import APIRouter, Depends, HTTPException
from app.db.session import get_db
from app.models.game import Game
from datetime import datetime

router = APIRouter()


@router.post("/notify-odds-update")
async def update_odds(request: UpdateOddsRequest, db: Session = Depends(get_db)):
    print(f'IN NOTIFYODDS UPDATE BY GAMEID {request.game_id}')
    if request.game_id:
        game_model = db.query(Game).filter(Game.game_id == request.game_id).first()
        if not game_model:
            raise HTTPException(status_code=404, detail="Game not found")
            
        # Convert SQLAlchemy model to Pydantic model
        game_data = GameResponse.model_validate(game_model)
        
        print(f'BROADCAST UPDATED ODDS TO REACT NOW...')
        # Broadcast update to all connected clients
        await odds_manager.broadcast_odds_update(
            game_id=request.game_id,
            game_data=game_data.dict(by_alias=True)  # Convert to dict with aliased field names
        )
    
    return {"status": "success"}

@router.post("/update-odds-by-teams/{home_team}/{away_team}/{game_date}")
async def update_odds_by_teams(
    request: UpdateOddsByTeamsRequest,
    db: Session = Depends(get_db)
):
    print(f'IN NOTIFY ODDS BY TEAMS: {request.away_team} AT {request.home_team} ON {request.game_date}')
    if request.away_team and request.home_team and request.game_date:
        date_obj = datetime.strptime(request.game_date, "%Y-%m-%d")
        updated_game = db.query(Game).filter(request.away_team == Game.away_team, request.home_team == Game.home_team, date_obj == Game.game_date)
        print(f'TEAMS AND GAME DATE NOT NULL, BROADCASTING TO REACT...')
        # Broadcast update to all connected clients
        await odds_manager.broadcast_odds_update_by_teams(
            home_team=request.home_team,
            away_team=request.away_team,
            game_date=request.game_date,
            game_data=updated_game
        )
    
    return {"status": "success"}