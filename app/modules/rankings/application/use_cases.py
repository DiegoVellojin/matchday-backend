from typing import List, Dict
from app.modules.rankings.domain.interfaces import IRankingRepository

class GetTeamLeaderboardUseCase:
    """Caso de uso para obtener la tabla de clasificación de equipos."""
    def __init__(self, repository: IRankingRepository):
        self.repository = repository

    def execute(self, sport_id: int | None = None) -> List[Dict]:
        return self.repository.get_team_leaderboard(sport_id=sport_id)

class EvaluateTeamUseCase:
    """Caso de uso para evaluar al equipo rival y su capitán."""
    def __init__(self, repository: IRankingRepository):
        self.repository = repository

    def execute(self, partida_id: int, evaluador_id: int, puntuacion: int, comentario: str | None = None) -> bool:
        # Primero verificamos si ya evaluó
        if self.repository.has_evaluated(partida_id, evaluador_id):
            return False
        return self.repository.evaluate_team(partida_id, evaluador_id, puntuacion, comentario)

class HasEvaluatedUseCase:
    """Caso de uso para verificar si un usuario ya evaluó un partido."""
    def __init__(self, repository: IRankingRepository):
        self.repository = repository

    def execute(self, partida_id: int, evaluador_id: int) -> bool:
        return self.repository.has_evaluated(partida_id, evaluador_id)

class GetEvaluationsUseCase:
    """Caso de uso para obtener las evaluaciones de un equipo o capitán."""
    def __init__(self, repository: IRankingRepository):
        self.repository = repository

    def execute(self, target_id: int, is_team: bool) -> List[Dict]:
        return self.repository.get_evaluations(target_id, is_team)
