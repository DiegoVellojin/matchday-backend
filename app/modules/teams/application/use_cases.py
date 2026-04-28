from typing import List, Optional
from app.modules.teams.domain.interfaces import IEquipoRepository
from app.modules.teams.domain.entities import Equipo, EquipoUsuario

class CreateTeamUseCase:
    """
    Caso de uso para crear un equipo. 
    Al crear un equipo, el usuario creador se convierte automáticamente 
    en el Capitán con estatus 'aceptado'.
    """
    def __init__(self, repository: IEquipoRepository):
        self.repository = repository

    def execute(
        self, 
        nombre: str, 
        id_deporte: int, 
        id_usuario_creador: int, 
        url_logo: Optional[str] = None,
        descripcion: Optional[str] = None,
        esta_reclutando: bool = True,
        max_miembros: int = 11
    ) -> Equipo:
        # 1. Crear el equipo
        nuevo_equipo = Equipo(
            id_equipo=None,
            nombre_equipo=nombre,
            fk_id_deporte=id_deporte,
            fk_id_usuario_capitan=id_usuario_creador,
            url_logo_equipo=url_logo,
            descripcion_equipo=descripcion,
            esta_reclutando=esta_reclutando,
            max_miembros=max_miembros
        )
        equipo_creado = self.repository.create(nuevo_equipo)

        # 2. Agregar al creador como miembro Capitán aceptado
        membresia = EquipoUsuario(
            fk_id_equipo=equipo_creado.id_equipo,
            fk_id_usuario=id_usuario_creador,
            estatus_miembro="aceptado",
            rol_equipo="Capitan"
        )
        self.repository.add_member(membresia)

        return equipo_creado

class RequestJoinTeamUseCase:
    """
    Caso de uso para solicitar unirse a un equipo.
    Crea una membresía con estatus 'pendiente'.
    """
    def __init__(self, repository: IEquipoRepository):
        self.repository = repository

    def execute(self, id_equipo: int, id_usuario: int) -> EquipoUsuario:
        # Aquí se podrían agregar validaciones: si ya es miembro, etc.
        membresia = EquipoUsuario(
            fk_id_equipo=id_equipo,
            fk_id_usuario=id_usuario,
            estatus_miembro="pendiente",
            rol_equipo="Jugador"
        )
        return self.repository.add_member(membresia)

class GetMyTeamsUseCase:
    """
    Caso de uso para obtener todos los equipos a los que pertenece el usuario.
    """
    def __init__(self, repository: IEquipoRepository):
        self.repository = repository

    def execute(self, id_usuario: int) -> List[Equipo]:
        return self.repository.get_teams_by_user(id_usuario)

class JoinTeamWithTokenUseCase:
    """
    Caso de uso para unirse a un equipo usando un token firmado.
    Si el token es válido, se une al usuario automáticamente como 'aceptado'.
    """
    def __init__(self, repository: IEquipoRepository):
        self.repository = repository

    def execute(self, token: str, id_usuario: int) -> EquipoUsuario:
        from app.core.security import verify_team_invitation_token
        
        id_equipo = verify_team_invitation_token(token)
        if not id_equipo:
            raise ValueError("El enlace de invitación es inválido o ha expirado.")

        # Verificar si ya es miembro
        miembros = self.repository.get_members(id_equipo)
        if any(m.fk_id_usuario == id_usuario for m in miembros):
            raise ValueError("Ya eres miembro de este equipo.")

        membresia = EquipoUsuario(
            fk_id_equipo=id_equipo,
            fk_id_usuario=id_usuario,
            estatus_miembro="aceptado", # Con el link entra directo
            rol_equipo="Jugador"
        )
        return self.repository.add_member(membresia)

class GetPendingMembersUseCase:
    """
    Caso de uso para obtener las solicitudes pendientes de un equipo.
    """
    def __init__(self, repository: IEquipoRepository):
        self.repository = repository

    def execute(self, id_equipo: int) -> List[EquipoUsuario]:
        miembros = self.repository.get_members(id_equipo)
        return [m for m in miembros if m.estatus_miembro == "pendiente"]

class RespondToJoinRequestUseCase:
    """
    Caso de uso para aceptar o rechazar una solicitud.
    Si se rechaza, se elimina de la base de datos para ahorrar espacio.
    """
    def __init__(self, repository: IEquipoRepository):
        self.repository = repository

    def execute(self, id_equipo: int, id_usuario: int, aceptar: bool) -> bool:
        if aceptar:
            return self.repository.update_member_status(
                id_equipo=id_equipo,
                id_usuario=id_usuario,
                status="aceptado",
                role="Jugador"
            )
        else:
            return self.repository.delete_member(id_equipo, id_usuario)

class GetDiscoverableTeamsUseCase:
    """
    Caso de uso para obtener todos los equipos que están reclutando miembros.
    """
    def __init__(self, repository: IEquipoRepository):
        self.repository = repository

    def execute(self) -> List[Equipo]:
        return self.repository.get_discoverable_teams()

