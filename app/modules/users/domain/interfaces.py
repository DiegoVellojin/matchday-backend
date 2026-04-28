from abc import ABC, abstractmethod
from typing import Optional
from app.modules.users.domain.entities import Usuario

class IUsuarioRepository(ABC):
    """
    Contrato/Interfaz para el repositorio de usuarios.
    Define los métodos que la infraestructura debe implementar.
    """
    @abstractmethod
    def get_by_id(self, id_usuario: int) -> Optional[Usuario]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def create(self, usuario: Usuario) -> Usuario:
        pass

    @abstractmethod
    def update(self, usuario: Usuario) -> Usuario:
        pass

class IFCMRepository(ABC):
    @abstractmethod
    def save_token(self, id_usuario: int, fcm_token: str) -> None:
        pass

    @abstractmethod
    def delete_token(self, fcm_token: str) -> None:
        pass

    @abstractmethod
    def get_tokens_by_user(self, id_usuario: int) -> list[str]:
        pass

