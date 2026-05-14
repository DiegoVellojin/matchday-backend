from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.modules.rankings.infrastructure.repositories_impl import RankingRepositoryImpl
from app.modules.rankings.application.use_cases import GetTeamLeaderboardUseCase

router = APIRouter(prefix="/rankings", tags=["Rankings"])

class LeaderboardEntry(BaseModel):
    posicion: int
    id_equipo: int
    nombre_equipo: str
    url_logo_equipo: str | None
    deporte: str
    puntos_totales: int
    partidos_jugados: int
    victorias: int
    empates: int
    derrotas: int

@router.get("/team-leaderboard", response_model=List[LeaderboardEntry])
def get_team_leaderboard(sport_id: int | None = None, db: Session = Depends(get_db)):
    """Obtiene la clasificación de los equipos filtrada opcionalmente por deporte."""
    repository = RankingRepositoryImpl(db)
    use_case = GetTeamLeaderboardUseCase(repository)
    return use_case.execute(sport_id=sport_id)
