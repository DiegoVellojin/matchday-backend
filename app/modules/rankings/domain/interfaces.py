from abc import ABC, abstractmethod
from typing import List, Dict

class IRankingRepository(ABC):
    """Interfaz para el repositorio de Rankings."""

    @abstractmethod
    def get_team_leaderboard(self, sport_id: int | None = None) -> List[Dict]:
        """Obtiene la tabla de clasificación de equipos."""
        pass

    @abstractmethod
    def evaluate_team(self, partida_id: int, evaluador_id: int, puntuacion: int, comentario: str | None = None) -> bool:
        """Registra una evaluación para el equipo rival y su capitán."""
        pass

    @abstractmethod
    def has_evaluated(self, partida_id: int, evaluador_id: int) -> bool:
        """Verifica si un usuario ya ha evaluado en un partido específico."""
        pass
