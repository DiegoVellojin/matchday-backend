from datetime import datetime
from typing import cast, List
from sqlalchemy.orm import Session
from app.modules.notifications.domain.entities import Notificacion
from app.modules.notifications.domain.interfaces import INotificationRepository
from app.modules.notifications.infrastructure.orm_models import NotificacionORM

class NotificationRepositoryImpl(INotificationRepository):
    """
    Implementación del repositorio de notificaciones utilizando SQLAlchemy.
    
    Gestiona la persistencia de las alertas y mensajes enviados a los usuarios, 
    así como su estado de lectura.
    """
    
    def __init__(self, db: Session):
        """
        :param db: Sesión de base de datos activa.
        """
        self.db = db

    def _to_entity(self, orm: NotificacionORM) -> Notificacion:
        """
        Convierte un modelo ORM de notificación a su entidad de dominio.
        
        :param orm: Objeto de base de datos.
        :return: Entidad Notificacion.
        """
        return Notificacion(
            id_notificacion=cast(int, orm.id_notificacion),
            fk_id_usuario=cast(int, orm.fk_id_usuario),
            mensaje=cast(str, orm.mensaje),
            leida=cast(bool, orm.leida),
            fecha_creacion=cast(datetime, orm.fecha_creacion),
            tipo=cast(str, orm.tipo),
            referencia_id=cast(int, orm.referencia_id)
        )

    def create(self, notificacion: Notificacion) -> Notificacion:
        """
        Registra una nueva notificación en la base de datos.
        
        :param notificacion: Datos de la notificación a crear.
        :return: Notificación persistida.
        """
        orm = NotificacionORM(
            fk_id_usuario=notificacion.fk_id_usuario,
            mensaje=notificacion.mensaje,
            leida=notificacion.leida,
            tipo=notificacion.tipo,
            referencia_id=notificacion.referencia_id
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def get_by_user(self, id_usuario: int) -> List[Notificacion]:
        """
        Recupera el historial completo de notificaciones de un usuario, 
        ordenado por fecha de creación descendente.
        
        :param id_usuario: ID del usuario.
        :return: Lista de notificaciones.
        """
        orms = self.db.query(NotificacionORM).filter(
            NotificacionORM.fk_id_usuario == id_usuario
        ).order_by(NotificacionORM.fecha_creacion.desc()).all()
        return [self._to_entity(orm) for orm in orms]

    def mark_as_read(self, id_notificacion: int, id_usuario: int) -> bool:
        """
        Establece una notificación específica como leída.
        
        :param id_notificacion: Identificador de la notificación.
        :param id_usuario: Identificador del usuario (por seguridad).
        :return: True si se encontró y actualizó la notificación.
        """
        orm = self.db.query(NotificacionORM).filter(
            NotificacionORM.id_notificacion == id_notificacion,
            NotificacionORM.fk_id_usuario == id_usuario
        ).first()
        if orm:
            setattr(orm, "leida", True)
            self.db.commit()
            return True
        return False

    def mark_all_as_read(self, id_usuario: int) -> bool:
        """
        Marca todas las notificaciones pendientes de un usuario como leídas en una sola transacción.
        
        :param id_usuario: Identificador del usuario.
        :return: True tras completar la operación.
        """
        orms = self.db.query(NotificacionORM).filter(
            NotificacionORM.fk_id_usuario == id_usuario,
            NotificacionORM.leida == False
        ).all()
        for orm in orms:
            setattr(orm, "leida", True)
        self.db.commit()
        return True
