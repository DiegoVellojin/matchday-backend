from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.modules.rankings.infrastructure.repositories_impl import RankingRepositoryImpl
from app.modules.rankings.application.use_cases import GetTeamLeaderboardUseCase, EvaluateTeamUseCase, HasEvaluatedUseCase
from app.core.security import get_current_user_id

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

class EvaluationRequest(BaseModel):
    partida_id: int
    puntuacion: int # 1-5
    comentario: str | None = None

@router.get("/team-leaderboard", response_model=List[LeaderboardEntry])
def get_team_leaderboard(sport_id: int | None = None, db: Session = Depends(get_db)):
    """Obtiene la clasificación de los equipos filtrada opcionalmente por deporte."""
    repository = RankingRepositoryImpl(db)
    use_case = GetTeamLeaderboardUseCase(repository)
    return use_case.execute(sport_id=sport_id)

@router.post("/evaluate")
def evaluate_team(request: EvaluationRequest, current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Registra una evaluación para el equipo rival."""
    repository = RankingRepositoryImpl(db)
    use_case = EvaluateTeamUseCase(repository)
    success = use_case.execute(
        partida_id=request.partida_id,
        evaluador_id=current_user_id,
        puntuacion=request.puntuacion,
        comentario=request.comentario
    )
    if not success:
        return {"status": "error", "message": "No se pudo registrar la evaluación o ya fue realizada."}
    return {"status": "success", "message": "Evaluación registrada correctamente."}

@router.get("/has-evaluated/{match_id}")
def check_evaluation(match_id: int, current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Verifica si el usuario ya evaluó este partido."""
    repository = RankingRepositoryImpl(db)
    use_case = HasEvaluatedUseCase(repository)
    has_evaluated = use_case.execute(partida_id=match_id, evaluador_id=current_user_id)
    return {"has_evaluated": has_evaluated}
