from typing import List
from app.modules.notifications.domain.interfaces import INotificacionRepository
from app.modules.notifications.domain.entities import Notificacion

class GetMyNotificationsUseCase:
    """
    Caso de uso para recuperar el historial de notificaciones de un usuario.
    """
    
    def __init__(self, repository: INotificacionRepository):
        """
        :param repository: Implementación del repositorio de notificaciones.
        """
        self.repository = repository

    def execute(self, id_usuario: int) -> List[Notificacion]:
        """
        Obtiene todas las notificaciones (leídas y no leídas) para el usuario.
        
        :param id_usuario: ID del usuario consultante.
        :return: Lista de entidades Notificacion.
        """
        return self.repository.get_by_user(id_usuario)

class MarkNotificationAsReadUseCase:
    """
    Caso de uso para marcar una notificación específica como leída.
    """
    
    def __init__(self, repository: INotificacionRepository):
        self.repository = repository

    def execute(self, id_notificacion: int, id_usuario: int) -> bool:
        """
        Cambia el estado de una notificación a 'leída'.
        
        :param id_notificacion: ID de la notificación.
        :param id_usuario: ID del dueño de la notificación (para validación).
        :return: True si se actualizó correctamente.
        """
        return self.repository.mark_as_read(id_notificacion, id_usuario)

class MarkAllNotificationsAsReadUseCase:
    """
    Caso de uso para marcar masivamente todas las notificaciones de un usuario como leídas.
    """
    
    def __init__(self, repository: INotificacionRepository):
        self.repository = repository

    def execute(self, id_usuario: int) -> bool:
        """
        Actualiza el estado 'leida' a True para todas las notificaciones del usuario.
        
        :param id_usuario: ID del usuario.
        :return: True si la operación fue exitosa.
        """
        return self.repository.mark_all_as_read(id_usuario)


class CreateNotificationUseCase:
    """
    Caso de uso para la creación y despacho de nuevas notificaciones.
    
    Gestiona tanto la persistencia en base de datos como el envío de 
    notificaciones push mediante Firebase Cloud Messaging (FCM).
    """
    
    def __init__(self, repository: INotificacionRepository):
        self.repository = repository

    def execute(self, id_usuario: int, mensaje: str, tipo: str = None, referencia_id: int = None, db = None) -> Notificacion:
        """
        Crea una notificación y opcionalmente envía un mensaje push.
        
        :param id_usuario: ID del destinatario.
        :param mensaje: Contenido de la notificación.
        :param tipo: Categoría (p.ej. 'join_request', 'match_invite').
        :param referencia_id: ID del objeto relacionado (equipo, partido).
        :param db: Sesión de DB (requerido para buscar tokens FCM).
        :return: La entidad Notificacion persistida.
        """
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
