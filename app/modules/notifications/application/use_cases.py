from typing import List
from app.modules.notifications.domain.interfaces import INotificacionRepository
from app.modules.notifications.domain.entities import Notificacion

class GetMyNotificationsUseCase:
    def __init__(self, repository: INotificacionRepository):
        self.repository = repository

    def execute(self, id_usuario: int) -> List[Notificacion]:
        return self.repository.get_by_user(id_usuario)

class MarkNotificationAsReadUseCase:
    def __init__(self, repository: INotificacionRepository):
        self.repository = repository

    def execute(self, id_notificacion: int, id_usuario: int) -> bool:
        return self.repository.mark_as_read(id_notificacion, id_usuario)

class CreateNotificationUseCase:
    def __init__(self, repository: INotificacionRepository):
        self.repository = repository

    def execute(self, id_usuario: int, mensaje: str, tipo: str = None, referencia_id: int = None) -> Notificacion:
        from datetime import datetime
        notif = Notificacion(
            id_notificacion=None,
            fk_id_usuario=id_usuario,
            mensaje=mensaje,
            leida=False,
            fecha_creacion=datetime.utcnow(),
            tipo=tipo,
            referencia_id=referencia_id
        )
        return self.repository.create(notif)
