from abc import ABC, abstractmethod
from typing import Optional
from app.modules.users.domain.entities import Usuario

class IUserRepository(ABC):
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

    @abstractmethod
    def update(self, usuario: Usuario) -> Usuario:
        """Actualiza un usuario existente en la base de datos."""
        pass
