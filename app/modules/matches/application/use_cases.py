from typing import List, Optional
from datetime import datetime
from app.modules.matches.domain.interfaces import IMatchRepository
from app.modules.matches.domain.entities import MatchEntity
from app.core.exceptions import NotFoundException, ConflictException, UnauthorizedException

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

    def execute(self, 
                sport_id: Optional[int] = None, 
                status: Optional[str] = "publicada",
                region_id: Optional[int] = None,
                cancha_id: Optional[int] = None,
                fecha: Optional[datetime] = None,
                user_id: Optional[int] = None,
                team_id: Optional[int] = None,
                exclude_user_id: Optional[int] = None) -> List[MatchEntity]:
        return self.repository.get_all(
            sport_id=sport_id, 
            status=status,
            region_id=region_id,
            cancha_id=cancha_id,
            fecha=fecha,
            user_id=user_id,
            team_id=team_id,
            exclude_user_id=exclude_user_id
        )

class GetMatchDetailsUseCase:
    """Caso de uso para obtener detalles de un partido."""
    def __init__(self, repository: IMatchRepository):
        self.repository = repository

    def execute(self, match_id: int) -> MatchEntity:
        match = self.repository.get_by_id(match_id)
        if not match:
            raise NotFoundException("Partido no encontrado")
        return match

class AcceptEncounterUseCase:
    """
    Caso de uso para aceptar un encuentro. 
    Cambia el estado a 'negociando' y asigna el equipo B.
    """
    def __init__(self, repository: IMatchRepository):
        self.repository = repository

    def execute(self, match_id: int, team_b_id: int) -> MatchEntity:
        match = self.repository.get_by_id(match_id)
        if not match:
            raise NotFoundException("Partido no encontrado")
        
        if match.estatus_partida != 'publicada':
            raise ConflictException("El partido ya no está disponible para ser aceptado")
            
        updated = self.repository.update(match_id, {
            "fk_id_equipo_b": team_b_id,
            "estatus_partida": "negociando"
        })
        if not updated:
            raise NotFoundException("Partido no encontrado tras la actualización")
        return updated

class ProposeTermsUseCase:
    """
    Caso de uso para proponer términos (hora y costo) por un capitán.
    Si ambos coinciden, el partido pasa a 'pendiente_pago'.
    """
    def __init__(self, repository: IMatchRepository):
        self.repository = repository

    def execute(self, match_id: int, user_id: int, fecha: datetime, costo: float, moneda: str) -> MatchEntity:
        match = self.repository.get_by_id(match_id)
        if not match:
            raise NotFoundException("Partido no encontrado")

        # Determinar si el usuario es capitán del equipo A o B
        is_captain_a = match.fk_id_usuario_org == user_id
        
        # Actualizar términos en repositorio
        updated_match = self.repository.update_terms(match_id, user_id, is_captain_a, fecha, costo, moneda)
        if not updated_match:
            raise NotFoundException("Partido no encontrado después de actualizar términos")

        # Verificar si hay coincidencia
        if updated_match.can_transition_to_pending_payment():
            assert updated_match.propuesta_fecha_a is not None and updated_match.propuesta_costo_a is not None
            self.repository.update(match_id, {
                "estatus_partida": "pendiente_pago",
                "fecha_acordada": updated_match.propuesta_fecha_a,
                "costo_total_partida": updated_match.propuesta_costo_a,
                "moneda": updated_match.propuesta_moneda_a
            })
            updated_match.estatus_partida = "pendiente_pago"
            updated_match.fecha_acordada = updated_match.propuesta_fecha_a
            updated_match.costo_total_partida = updated_match.propuesta_costo_a

        return updated_match

class ConfigureMatchUseCase:
    """
    Caso de uso para que el capitán configure el partido y registre datos bancarios.
    """
    def __init__(self, repository: IMatchRepository):
        self.repository = repository

    def execute(self, match_id: int, user_id: int, fecha: datetime, costo: float, moneda: str, banco: str, cedula: str, telefono: str) -> MatchEntity:
        match = self.repository.get_by_id(match_id)
        if not match:
            raise NotFoundException("Partido no encontrado")
        # Verificar que el usuario sea capitán de alguno de los equipos (org o alguien más)
        configured = self.repository.configure_match(match_id, user_id, fecha, costo, moneda, banco, cedula, telefono)
        if not configured:
            raise NotFoundException("Partido no encontrado al configurar")
        return configured

class MarkTeamReadyUseCase:
    """
    Verifica que todos los jugadores de un equipo estén verificados y lo marca como listo.
    """
    def __init__(self, match_repository: IMatchRepository):
        self.match_repository = match_repository

    def execute(self, match_id: int, current_user_id: int) -> MatchEntity:
        match = self.match_repository.get_by_id(match_id)
        if not match:
            raise NotFoundException("Partido no encontrado")
            
        # Determinar qué equipo lidera el usuario actual
        team_id = None
        if match.fk_id_usuario_org == current_user_id:
            team_id = match.fk_id_equipo_a
        else:
            team_id = match.fk_id_equipo_b
            
        if team_id is None:
            raise ConflictException("No se determinó tu equipo o el partido no tiene equipos.")
            
        # Verificar que todos los jugadores del team_id en PartidaUsuario tengan estatus_pago = verificado
        players = self.match_repository.get_players(match_id)
        team_players = [p for p in players if p["id_equipo"] == team_id]
        
        # Omitimos al capitán mismo (no se paga a sí mismo). El capitán es current_user_id
        for p in team_players:
            if p["id_usuario"] != current_user_id and p["estatus_pago"] != 'verificado':
                raise ConflictException("Aún hay jugadores sin pago verificado en tu equipo.")
                
        # Si llegamos aquí, todos están verificados
        updated_match = self.match_repository.mark_team_ready(match_id, team_id)
        if not updated_match:
            raise NotFoundException("Partido no encontrado al marcar equipo listo")
        return updated_match

class JoinMatchUseCase:
    """Caso de uso para que un usuario se una a un partido."""
    def __init__(self, repository: IMatchRepository):
        self.repository = repository

    def execute(self, match_id: int, user_id: int, team_id: Optional[int] = None) -> bool:
        match = self.repository.get_by_id(match_id)
        if not match:
            raise NotFoundException("Partido no encontrado")
        return self.repository.add_player(match_id, user_id, team_id)

class RegisterMatchResultUseCase:
    """Caso de uso para registrar un resultado."""
    def __init__(self, repository: IMatchRepository):
        self.repository = repository

    def execute(self, match_id: int, current_user_id: int, goals_a: int, goals_b: int) -> None:
        match = self.repository.get_by_id(match_id)
        if not match:
            raise NotFoundException("Partido no encontrado")
            
        if match.estatus_partida != 'confirmada':
            raise ConflictException("El partido debe estar 'confirmada' para registrar un resultado")
            
        if not match.fk_id_equipo_a or not match.fk_id_equipo_b:
            raise ConflictException("El partido debe tener dos equipos para registrar un resultado")

        # El usuario debe ser uno de los capitanes
        is_cap_a = match.fk_id_usuario_org == current_user_id
        # Para simplificar, asumimos que si no es cap_a, validamos si es el capitan b. 
        # En la bd, el cap_b es el organizador de equipo_b, por simplicidad dejaremos que intente
        # submit_result_proposal (el repo ya revisa fk_id_usuario_org).
        
        updated_match = self.repository.submit_result_proposal(match_id, current_user_id, goals_a, goals_b)
        if not updated_match:
            raise NotFoundException("Partido no encontrado al registrar el resultado")
        
        # Verificación Cruzada
        if updated_match.resultado_goles_a_cap_a is not None and updated_match.resultado_goles_a_cap_b is not None:
            if updated_match.fk_id_equipo_a is None or updated_match.fk_id_equipo_b is None:
                raise ConflictException("No se puede registrar resultado sin ambos equipos asignados.")

            if (updated_match.resultado_goles_a_cap_a == updated_match.resultado_goles_a_cap_b and
                updated_match.resultado_goles_b_cap_a == updated_match.resultado_goles_b_cap_b):
                # Hay coincidencia! Registrar resultado oficial
                assert updated_match.fk_id_equipo_a is not None
                assert updated_match.fk_id_equipo_b is not None
                assert updated_match.resultado_goles_a_cap_a is not None
                assert updated_match.resultado_goles_b_cap_a is not None
                self.repository.register_result(
                    match_id, 
                    updated_match.fk_id_equipo_a, 
                    updated_match.fk_id_equipo_b, 
                    updated_match.resultado_goles_a_cap_a, 
                    updated_match.resultado_goles_b_cap_a
                )
            else:
                # Discrepancia
                raise ConflictException("Hay una discrepancia en los resultados ingresados por ambos capitanes. Revisa de nuevo.")
        else:
            # Aún falta que el otro capitán ingrese
            pass

class GetMatchPlayersUseCase:
    """Caso de uso para obtener los jugadores unidos a un partido."""
    def __init__(self, repository: IMatchRepository):
        self.repository = repository

    def execute(self, match_id: int) -> List[dict]:
        match = self.repository.get_by_id(match_id)
        if not match:
            raise NotFoundException("Partido no encontrado")
        return self.repository.get_players(match_id)
