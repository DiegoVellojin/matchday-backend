from abc import ABC, abstractmethod
from typing import List, Dict

class IRankingRepository(ABC):
    """Interfaz para el repositorio de Rankings."""

    @abstractmethod
    def get_team_leaderboard(self) -> List[Dict]:
        """Obtiene la tabla de clasificación de equipos ordenados por puntos."""
        pass
