from app.modules.users.domain.interfaces import IUsuarioRepository
from app.modules.users.domain.entities import Usuario
from typing import Optional

class GetUserProfileUseCase:
    """
    Caso de uso para obtener el perfil del usuario actual.
    """
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository

    def execute(self, id_usuario: int) -> Optional[Usuario]:
        return self.usuario_repository.get_by_id(id_usuario)

class UpdateUserProfileUseCase:
    """
    Caso de uso para actualizar los datos del perfil (nombre, teléfono, foto).
    """
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository

    def execute(self, id_usuario: int, nombre: Optional[str] = None, telefono: Optional[str] = None, foto_url: Optional[str] = None) -> Usuario:
        usuario = self.usuario_repository.get_by_id(id_usuario)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        if nombre:
            usuario.nombre_usuario = nombre
        if telefono:
            usuario.telefono_usuario = telefono
        if foto_url:
            usuario.url_foto_perfil = foto_url

        return self.usuario_repository.update(usuario)
