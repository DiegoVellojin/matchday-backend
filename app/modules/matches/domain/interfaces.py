from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from app.modules.matches.domain.entities import MatchEntity

class IMatchRepository(ABC):
    """Interfaz para el repositorio de partidos."""

    @abstractmethod
    def create(self, match: MatchEntity) -> MatchEntity:
        """Crea un nuevo partido."""
        pass

    @abstractmethod
    def get_by_id(self, match_id: int) -> Optional[MatchEntity]:
        """Obtiene un partido por su ID."""
        pass

    @abstractmethod
    def get_all(self, 
                sport_id: Optional[int] = None, 
                status: Optional[str] = None,
                region_id: Optional[int] = None,
                cancha_id: Optional[int] = None,
                fecha: Optional[datetime] = None) -> List[MatchEntity]:
        """Obtiene todos los partidos con filtros opcionales."""
        pass

    @abstractmethod
    def update(self, match_id: int, data: dict) -> Optional[MatchEntity]:
        """Actualiza un partido."""
        pass

    @abstractmethod
    def add_player(self, match_id: int, user_id: int, team_id: Optional[int] = None) -> bool:
        """Añade un jugador a un partido."""
        pass

    @abstractmethod
    def get_players(self, match_id: int) -> List[dict]:
        """Obtiene la lista de jugadores de un partido."""
        pass

    @abstractmethod
    def update_terms(self, match_id: int, user_id: int, is_captain_a: bool, fecha: datetime, costo: float) -> MatchEntity:
        """Actualiza los términos propuestos por un capitán."""
        pass
