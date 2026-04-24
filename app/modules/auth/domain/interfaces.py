from abc import ABC, abstractmethod
from typing import Optional
from app.modules.auth.domain.entities import Usuario

class IUsuarioRepository(ABC):
    """
    Contrato (Puerto) para el repositorio de Usuarios.
    Define las operaciones permitidas sin saber cómo se implementan (Base de datos).
    """
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Usuario]:
        """Busca un usuario por su correo electrónico."""
        pass

    @abstractmethod
    def create(self, usuario: Usuario) -> Usuario:
        """Crea un nuevo usuario y retorna la entidad con el ID asignado."""
        pass
