from app.modules.users.domain.interfaces import IUserRepository
from app.modules.users.domain.entities import Usuario
from typing import Optional
from app.core.security import get_password_hash


class GetUserProfileUseCase:
    """
    Caso de uso para recuperar la información de perfil de un usuario.
    """
    
    def __init__(self, usuario_repository: IUserRepository):
        """
        :param usuario_repository: Implementación del repositorio de usuarios.
        """
        self.usuario_repository = usuario_repository

    def execute(self, id_usuario: int) -> Optional[Usuario]:
        """
        Consulta los datos del usuario por su identificador único.
        
        :param id_usuario: ID del usuario a consultar.
        :return: Entidad Usuario o None si no existe.
        """
        return self.usuario_repository.get_by_id(id_usuario)

class UpdateUserProfileUseCase:
    """
    Caso de uso para modificar la información del perfil del usuario.
    
    Permite actualizaciones parciales de campos como nombre, teléfono, 
    foto de perfil y contraseña.
    """
    
    def __init__(self, usuario_repository: IUserRepository):
        """
        :param usuario_repository: Implementación del repositorio de usuarios.
        """
        self.usuario_repository = usuario_repository

    def execute(
        self, 
        id_usuario: int, 
        nombre: Optional[str] = None, 
        telefono: Optional[str] = None, 
        foto_url: Optional[str] = None, 
        password: Optional[str] = None
    ) -> Usuario:
        """
        Aplica los cambios solicitados al perfil del usuario.
        
        :param id_usuario: ID del usuario a actualizar.
        :param nombre: Nuevo nombre (opcional).
        :param telefono: Nuevo teléfono (opcional).
        :param foto_url: Nueva URL de foto de perfil (opcional).
        :param password: Nueva contraseña en texto plano (opcional, será hasheada).
        :raises NotFoundException: Si el usuario no existe en el sistema.
        :return: La entidad Usuario actualizada.
        """
        usuario = self.usuario_repository.get_by_id(id_usuario)
        if not usuario:
            from app.core.exceptions import NotFoundException
            raise NotFoundException("Usuario no encontrado")

        if nombre:
            usuario.nombre_usuario = nombre
        if telefono:
            usuario.telefono_usuario = telefono
        if foto_url:
            usuario.url_foto_perfil = foto_url
        if password:
            usuario.password_hash = get_password_hash(password)

        return self.usuario_repository.update(usuario)
