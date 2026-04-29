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

class MarkAllNotificationsAsReadUseCase:
    def __init__(self, repository: INotificacionRepository):
        self.repository = repository

    def execute(self, id_usuario: int) -> bool:
        return self.repository.mark_all_as_read(id_usuario)


class CreateNotificationUseCase:
    def __init__(self, repository: INotificacionRepository):
        self.repository = repository

    def execute(self, id_usuario: int, mensaje: str, tipo: str = None, referencia_id: int = None, db = None) -> Notificacion:
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
        saved_notif = self.repository.create(notif)
        
        if db:
            try:
                from app.modules.users.infrastructure.repositories_impl import FCMRepositoryImpl
                from firebase_admin import messaging
                
                fcm_repo = FCMRepositoryImpl(db)
                tokens = fcm_repo.get_tokens_by_user(id_usuario)
                
                if tokens:
                    for token in tokens:
                        try:
                            message = messaging.Message(
                                notification=messaging.Notification(
                                    title="MatchDay ⚽",
                                    body=mensaje,
                                ),
                                token=token,
                            )
                            messaging.send(message)
                        except Exception as e_send:
                            print(f"Error enviando token individual {token}: {e_send}")

            except Exception as e:
                print(f"Error al enviar notificación push FCM: {e}")
                
        return saved_notif

