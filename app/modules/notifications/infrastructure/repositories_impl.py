from typing import List
from sqlalchemy.orm import Session
from app.modules.notifications.domain.entities import Notificacion
from app.modules.notifications.domain.interfaces import INotificacionRepository
from app.modules.notifications.infrastructure.orm_models import NotificacionORM

class NotificacionRepositoryImpl(INotificacionRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, orm: NotificacionORM) -> Notificacion:
        return Notificacion(
            id_notificacion=orm.id_notificacion,
            fk_id_usuario=orm.fk_id_usuario,
            mensaje=orm.mensaje,
            leida=orm.leida,
            fecha_creacion=orm.fecha_creacion,
            tipo=orm.tipo,
            referencia_id=orm.referencia_id
        )

    def create(self, notificacion: Notificacion) -> Notificacion:
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
        orms = self.db.query(NotificacionORM).filter(
            NotificacionORM.fk_id_usuario == id_usuario
        ).order_by(NotificacionORM.fecha_creacion.desc()).all()
        return [self._to_entity(orm) for orm in orms]

    def mark_as_read(self, id_notificacion: int, id_usuario: int) -> bool:
        orm = self.db.query(NotificacionORM).filter(
            NotificacionORM.id_notificacion == id_notificacion,
            NotificacionORM.fk_id_usuario == id_usuario
        ).first()
        if orm:
            orm.leida = True
            self.db.commit()
            return True
        return False
