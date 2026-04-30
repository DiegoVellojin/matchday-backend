from abc import ABC, abstractmethod
from typing import Optional, List
from app.modules.teams.domain.entities import Equipo, EquipoUsuario

class IEquipoRepository(ABC):
    """
    Interfaz para el repositorio de equipos.
    """
    @abstractmethod
    def create(self, equipo: Equipo) -> Equipo:
        pass

    @abstractmethod
    def get_by_id(self, id_equipo: int) -> Optional[Equipo]:
        pass

    @abstractmethod
    def add_member(self, membership: EquipoUsuario) -> EquipoUsuario:
        pass

    @abstractmethod
    def update_member_status(self, id_equipo: int, id_usuario: int, status: str, role: str) -> bool:
        pass

    @abstractmethod
    def get_members(self, id_equipo: int) -> List[EquipoUsuario]:
        pass

    @abstractmethod
    def get_teams_by_user(self, id_usuario: int) -> List[Equipo]:
        pass

    @abstractmethod
    def get_discoverable_teams(self) -> List[Equipo]:
        pass

    @abstractmethod
    def delete_member(self, id_equipo: int, id_usuario: int) -> bool:
        pass

    @abstractmethod
    def update(self, id_equipo: int, data: dict) -> Optional[Equipo]:
        pass

    @abstractmethod
    def delete(self, id_equipo: int) -> bool:
        pass

    @abstractmethod
    def transfer_captain(self, id_equipo: int, id_nuevo_capitan: int) -> bool:
        pass


