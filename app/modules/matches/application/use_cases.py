from typing import List, Optional
from datetime import datetime
from app.modules.matches.domain.interfaces import IMatchRepository
from app.modules.matches.domain.entities import MatchEntity

class CreateMatchUseCase:
    """Caso de uso para crear un nuevo partido."""
    def __init__(self, repository: IMatchRepository):
        self.repository = repository

    def execute(self, match_data: dict) -> MatchEntity:
        # Convertir datos de dict a entidad
        match = MatchEntity(**match_data)
        return self.repository.create(match)

class GetMatchesUseCase:
    """Caso de uso para listar partidos con filtros."""
    def __init__(self, repository: IMatchRepository):
        self.repository = repository

    def execute(self, sport_id: Optional[int] = None, status: Optional[str] = "publicada") -> List[MatchEntity]:
        return self.repository.get_all(sport_id=sport_id, status=status)

class GetMatchDetailsUseCase:
    """Caso de uso para obtener detalles de un partido."""
    def __init__(self, repository: IMatchRepository):
        self.repository = repository

    def execute(self, match_id: int) -> Optional[MatchEntity]:
        return self.repository.get_by_id(match_id)

class AcceptEncounterUseCase:
    """
    Caso de uso para aceptar un encuentro. 
    Cambia el estado a 'negociando' y asigna el equipo B.
    """
    def __init__(self, repository: IMatchRepository):
        self.repository = repository

    def execute(self, match_id: int, team_b_id: int) -> Optional[MatchEntity]:
        return self.repository.update(match_id, {
            "fk_id_equipo_b": team_b_id,
            "estatus_partida": "negociando"
        })

class ProposeTermsUseCase:
    """
    Caso de uso para proponer términos (hora y costo) por un capitán.
    Si ambos coinciden, el partido pasa a 'pendiente_pago'.
    """
    def __init__(self, repository: IMatchRepository):
        self.repository = repository

    def execute(self, match_id: int, user_id: int, fecha: datetime, costo: float) -> MatchEntity:
        match = self.repository.get_by_id(match_id)
        if not match:
            raise ValueError("Partido no encontrado")

        # Determinar si el usuario es capitán del equipo A o B
        is_captain_a = match.fk_id_usuario_org == user_id
        
        # Actualizar términos en repositorio
        updated_match = self.repository.update_terms(match_id, user_id, is_captain_a, fecha, costo)

        # Verificar si hay coincidencia
        if updated_match.can_transition_to_pending_payment():
            self.repository.update(match_id, {
                "estatus_partida": "pendiente_pago",
                "fecha_acordada": updated_match.propuesta_fecha_a,
                "costo_total_partida": updated_match.propuesta_costo_a
            })
            updated_match.estatus_partida = "pendiente_pago"
            updated_match.fecha_acordada = updated_match.propuesta_fecha_a
            updated_match.costo_total_partida = updated_match.propuesta_costo_a

        return updated_match

class JoinMatchUseCase:
    """Caso de uso para que un usuario se una a un partido."""
    def __init__(self, repository: IMatchRepository):
        self.repository = repository

    def execute(self, match_id: int, user_id: int, team_id: Optional[int] = None) -> bool:
        return self.repository.add_player(match_id, user_id, team_id)
