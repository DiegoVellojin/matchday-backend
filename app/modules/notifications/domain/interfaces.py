from abc import ABC, abstractmethod
from typing import List, Optional
from app.modules.notifications.domain.entities import Notificacion

class INotificacionRepository(ABC):
    @abstractmethod
    def create(self, notificacion: Notificacion) -> Notificacion:
        pass

    @abstractmethod
    def get_by_user(self, id_usuario: int) -> List[Notificacion]:
        pass

    @abstractmethod
    def mark_as_read(self, id_notificacion: int, id_usuario: int) -> bool:
        pass

    @abstractmethod
    def mark_all_as_read(self, id_usuario: int) -> bool:
        pass

