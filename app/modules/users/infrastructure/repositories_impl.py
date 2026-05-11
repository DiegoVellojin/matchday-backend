from datetime import datetime
from typing import cast, Optional
from sqlalchemy.orm import Session
from app.modules.users.domain.entities import Usuario
from app.modules.users.domain.interfaces import IUserRepository
from app.modules.users.infrastructure.orm_models import UsuarioORM
from app.modules.matches.infrastructure.orm_models import PartidaORM, PartidaUsuarioORM

class UserRepositoryImpl(IUserRepository):
    """
    Implementación concreta del repositorio de usuarios utilizando SQLAlchemy.
    """
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, orm_model: UsuarioORM) -> Usuario:
        """Convierte el modelo ORM de SQLAlchemy a la Entidad de Dominio."""
        return Usuario(
            id_usuario=cast(int, orm_model.id_usuario),
            nombre_usuario=cast(str, orm_model.nombre_usuario),
            email_usuario=cast(str, orm_model.email_usuario),
            password_hash=cast(str, orm_model.password_hash),
            telefono_usuario=cast(Optional[str], orm_model.telefono_usuario),
            url_foto_perfil=cast(Optional[str], orm_model.url_foto_perfil),
            rol_usuario=cast(str, orm_model.rol_usuario),
            reliability_score=cast(float, orm_model.reliability_score),
            fecha_creacion_usuario=cast(Optional[datetime], orm_model.fecha_creacion_usuario)
        )

    def _add_stats(self, orm_user: UsuarioORM) -> Usuario:
        """Calcula y agrega las estadísticas al usuario."""
        # Un partido cuenta como "jugado" solo si está 'completada'
        # Y el usuario fue el organizador O participó en él.
        partidos_jugados = self.db.query(PartidaORM).outerjoin(
            PartidaUsuarioORM, PartidaORM.id_partida == PartidaUsuarioORM.fk_id_partida
        ).filter(
            PartidaORM.estatus_partida == 'completada'
        ).filter(
            (PartidaORM.fk_id_usuario_org == orm_user.id_usuario) | 
            (PartidaUsuarioORM.fk_id_usuario == orm_user.id_usuario)
        ).distinct().count()

        # Partidos organizados: Todos los que no estén cancelados
        partidos_organizados = self.db.query(PartidaORM).filter(
            PartidaORM.fk_id_usuario_org == orm_user.id_usuario,
            PartidaORM.estatus_partida != 'cancelada'
        ).count()

        entity = self._to_entity(orm_user)
        entity.partidos_jugados = partidos_jugados
        entity.partidos_organizados = partidos_organizados
        return entity

    def get_by_id(self, id_usuario: int) -> Optional[Usuario]:
        orm_user = self.db.query(UsuarioORM).filter(UsuarioORM.id_usuario == id_usuario).first()
        if orm_user:
            return self._add_stats(orm_user)
        return None

    def get_by_email(self, email: str) -> Optional[Usuario]:
        orm_user = self.db.query(UsuarioORM).filter(UsuarioORM.email_usuario == email).first()
        if orm_user:
            return self._add_stats(orm_user)
        return None

    def create(self, usuario: Usuario) -> Usuario:
        orm_user = UsuarioORM(
            nombre_usuario=usuario.nombre_usuario,
            email_usuario=usuario.email_usuario,
            password_hash=usuario.password_hash,
            telefono_usuario=usuario.telefono_usuario,
            url_foto_perfil=usuario.url_foto_perfil,
            rol_usuario=usuario.rol_usuario,
            reliability_score=usuario.reliability_score
        )
        self.db.add(orm_user)
        self.db.commit()
        self.db.refresh(orm_user)
        return self._to_entity(orm_user)

    def update(self, usuario: Usuario) -> Usuario:
        orm_user = self.db.query(UsuarioORM).filter(UsuarioORM.id_usuario == usuario.id_usuario).first()
        if orm_user:
            setattr(orm_user, "nombre_usuario", usuario.nombre_usuario)
            setattr(orm_user, "telefono_usuario", usuario.telefono_usuario)
            setattr(orm_user, "url_foto_perfil", usuario.url_foto_perfil)
            # rol_usuario y reliability_score podrían no actualizarse desde este caso de uso simple
            if usuario.password_hash:
                setattr(orm_user, "password_hash", usuario.password_hash)
            
            self.db.commit()
            self.db.refresh(orm_user)
            return self._add_stats(orm_user)
        raise ValueError("Usuario no encontrado para actualizar")

from app.modules.users.domain.interfaces import IFCMRepository
from app.modules.users.infrastructure.orm_models import UsuarioFCMORM

class FCMRepositoryImpl(IFCMRepository):
    """
    Implementación del repositorio para guardar/borrar tokens FCM.
    """
    def __init__(self, db: Session):
        self.db = db

    def save_token(self, id_usuario: int, fcm_token: str) -> None:
        existing = self.db.query(UsuarioFCMORM).filter(UsuarioFCMORM.fcm_token == fcm_token).first()
        if existing:
            if cast(int, existing.fk_id_usuario) != id_usuario:
                setattr(existing, "fk_id_usuario", id_usuario)
                self.db.commit()
            return
        
        new_fcm = UsuarioFCMORM(
            fk_id_usuario=id_usuario,
            fcm_token=fcm_token
        )
        self.db.add(new_fcm)
        self.db.commit()

    def delete_token(self, fcm_token: str) -> None:
        token_to_delete = self.db.query(UsuarioFCMORM).filter(UsuarioFCMORM.fcm_token == fcm_token).first()
        if token_to_delete:
            self.db.delete(token_to_delete)
            self.db.commit()

    def get_tokens_by_user(self, id_usuario: int) -> list[str]:
        records = self.db.query(UsuarioFCMORM).filter(UsuarioFCMORM.fk_id_usuario == id_usuario).all()
        return [cast(str, r.fcm_token) for r in records]

