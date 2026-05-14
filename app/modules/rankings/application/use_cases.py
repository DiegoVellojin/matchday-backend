from typing import List, Dict
from app.modules.rankings.domain.interfaces import IRankingRepository

class GetTeamLeaderboardUseCase:
    """Caso de uso para obtener la tabla de clasificación de equipos."""
    def __init__(self, repository: IRankingRepository):
        self.repository = repository

    def execute(self, sport_id: int | None = None) -> List[Dict]:
        return self.repository.get_team_leaderboard(sport_id=sport_id)
