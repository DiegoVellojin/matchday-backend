from typing import List, Optional
from app.modules.teams.domain.interfaces import IEquipoRepository
from app.modules.teams.domain.entities import Equipo, EquipoUsuario

class CreateTeamUseCase:
    """
    Caso de uso encargado de la creación de nuevos equipos.
    
    Al crear un equipo, el sistema asigna automáticamente al usuario creador 
    como el Capitán del equipo con estatus de membresía 'aceptado'.
    """
    
    def __init__(self, repository: IEquipoRepository):
        """
        Inicializa el caso de uso con el repositorio de equipos.
        
        :param repository: Implementación del repositorio de equipos.
        """
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
        """
        Ejecuta la lógica para crear un equipo y registrar a su capitán.
        
        :param nombre: Nombre del equipo.
        :param id_deporte: ID del deporte asociado.
        :param id_usuario_creador: ID del usuario que crea el equipo (será Capitán).
        :param url_logo: URL opcional de la imagen o emoji del logo.
        :param descripcion: Descripción opcional del equipo.
        :param esta_reclutando: Indica si el equipo acepta nuevas solicitudes.
        :param max_miembros: Capacidad máxima de jugadores.
        :return: La entidad del equipo creado.
        """
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
    Caso de uso para gestionar las solicitudes de unión a un equipo.
    
    Crea un registro de membresía con estatus 'pendiente' que debe ser 
    aprobado por el capitán del equipo.
    """
    
    def __init__(self, repository: IEquipoRepository):
        """
        :param repository: Implementación del repositorio de equipos.
        """
        self.repository = repository

    def execute(self, id_equipo: int, id_usuario: int) -> EquipoUsuario:
        """
        Registra una solicitud de unión validando que el usuario no sea ya miembro.
        
        :param id_equipo: ID del equipo al que se desea unir.
        :param id_usuario: ID del usuario que solicita la unión.
        :raises ValueError: Si el usuario ya pertenece al equipo o tiene solicitud previa.
        :return: La entidad de membresía creada.
        """
        # Verificar si ya es miembro o tiene solicitud pendiente
        miembros = self.repository.get_members(id_equipo)
        if any(m.fk_id_usuario == id_usuario for m in miembros):
            raise ValueError("Ya eres miembro de este equipo o tienes una solicitud pendiente.")

        membresia = EquipoUsuario(
            fk_id_equipo=id_equipo,
            fk_id_usuario=id_usuario,
            estatus_miembro="pendiente",
            rol_equipo="Jugador"
        )
        return self.repository.add_member(membresia)


class GetMyTeamsUseCase:
    """
    Caso de uso para recuperar los equipos vinculados a un usuario específico.
    """
    
    def __init__(self, repository: IEquipoRepository):
        self.repository = repository

    def execute(self, id_usuario: int) -> List[Equipo]:
        """
        Consulta todos los equipos donde el usuario es miembro aceptado.
        
        :param id_usuario: ID del usuario consultante.
        :return: Lista de entidades de tipo Equipo.
        """
        return self.repository.get_teams_by_user(id_usuario)

class JoinTeamWithTokenUseCase:
    """
    Caso de uso para unirse a un equipo de forma directa mediante un enlace/token.
    
    A diferencia de la solicitud manual, el uso de un token válido garantiza 
    la entrada inmediata como miembro 'aceptado'.
    """
    
    def __init__(self, repository: IEquipoRepository):
        self.repository = repository

    def execute(self, token: str, id_usuario: int) -> EquipoUsuario:
        """
        Valida el token y registra al usuario como miembro aceptado.
        
        :param token: Token de invitación firmado.
        :param id_usuario: ID del usuario que usa el token.
        :raises ValueError: Si el token es inválido, expirado o el usuario ya es miembro.
        :return: La entidad de membresía creada.
        """
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
    Caso de uso para listar las solicitudes de unión que aguardan aprobación.
    """
    
    def __init__(self, repository: IEquipoRepository):
        self.repository = repository

    def execute(self, id_equipo: int) -> List[EquipoUsuario]:
        """
        Filtra los miembros del equipo por el estatus 'pendiente'.
        
        :param id_equipo: ID del equipo a consultar.
        :return: Lista de membresías pendientes.
        """
        miembros = self.repository.get_members(id_equipo)
        return [m for m in miembros if m.estatus_miembro == "pendiente"]

class RespondToJoinRequestUseCase:
    """
    Caso de uso para procesar la respuesta del capitán a una solicitud de unión.
    """
    
    def __init__(self, repository: IEquipoRepository):
        self.repository = repository

    def execute(self, id_equipo: int, id_usuario: int, aceptar: bool) -> bool:
        """
        Acepta o rechaza la solicitud. En caso de rechazo, se elimina el registro.
        
        :param id_equipo: ID del equipo.
        :param id_usuario: ID del jugador solicitante.
        :param aceptar: True para aprobar, False para denegar.
        :return: True si la operación fue exitosa.
        """
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
    Caso de uso para obtener todos los equipos con reclutamiento activo.
    """
    
    def __init__(self, repository: IEquipoRepository):
        self.repository = repository

    def execute(self) -> List[Equipo]:
        """
        Retorna la lista de equipos que tienen el flag 'esta_reclutando' en True.
        
        :return: Lista de equipos descubribles.
        """
        return self.repository.get_discoverable_teams()

class UpdateTeamUseCase:
    """
    Caso de uso para modificar los metadatos de un equipo existente.
    """
    
    def __init__(self, repository: IEquipoRepository):
        self.repository = repository

    def execute(self, id_equipo: int, data: dict) -> Optional[Equipo]:
        """
        Actualiza campos específicos (nombre, logo, etc.) de un equipo.
        
        :param id_equipo: ID del equipo a modificar.
        :param data: Diccionario con los campos y valores a actualizar.
        :return: La entidad del equipo actualizada o None si falló.
        """
        return self.repository.update(id_equipo, data)

class DeleteTeamUseCase:
    """
    Caso de uso para la eliminación definitiva de un equipo y sus datos asociados.
    """
    
    def __init__(self, repository: IEquipoRepository):
        self.repository = repository

    def execute(self, id_equipo: int) -> bool:
        """
        Elimina el equipo y limpia la relación de miembros.
        
        :param id_equipo: ID del equipo a eliminar.
        :return: True si la eliminación se completó satisfactoriamente.
        """
        return self.repository.delete(id_equipo)

class TransferCaptainUseCase:
    """
    Caso de uso para ceder el rol de capitán a otro miembro del equipo.
    """
    
    def __init__(self, repository: IEquipoRepository):
        self.repository = repository

    def execute(self, id_equipo: int, id_nuevo_capitan: int) -> bool:
        """
        Realiza el cambio de roles en la base de datos entre el antiguo y el nuevo capitán.
        
        :param id_equipo: ID del equipo afectado.
        :param id_nuevo_capitan: ID del usuario que asumirá la capitanía.
        :return: True si la transferencia fue exitosa.
        """
        return self.repository.transfer_captain(id_equipo, id_nuevo_capitan)
