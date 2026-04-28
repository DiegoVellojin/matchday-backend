from typing import Optional, List
from sqlalchemy.orm import Session
from app.modules.teams.domain.entities import Equipo, EquipoUsuario
from app.modules.teams.domain.interfaces import IEquipoRepository
from app.modules.teams.infrastructure.orm_models import EquipoORM, EquipoUsuarioORM
from app.modules.catalogs.domain.entities import Deporte
from app.modules.catalogs.infrastructure.orm_models import DeporteORM

class EquipoRepositoryImpl(IEquipoRepository):
    """
    Implementación del repositorio de equipos usando SQLAlchemy.
    """
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, orm: EquipoORM, deporte: Optional[Deporte] = None) -> Equipo:
        return Equipo(
            id_equipo=orm.id_equipo,
            nombre_equipo=orm.nombre_equipo,
            fk_id_deporte=orm.fk_id_deporte,
            fk_id_usuario_capitan=orm.fk_id_usuario_capitan,
            deporte=deporte,
            url_logo_equipo=orm.url_logo_equipo,
            puntos_acumulados=orm.puntos_acumulados,
            descripcion_equipo=orm.descripcion_equipo,
            esta_reclutando=orm.esta_reclutando,
            max_miembros=orm.max_miembros,
            fecha_creacion_equipo=orm.fecha_creacion_equipo
        )

    def _to_membership_entity(self, orm: EquipoUsuarioORM) -> EquipoUsuario:
        return EquipoUsuario(
            fk_id_equipo=orm.fk_id_equipo,
            fk_id_usuario=orm.fk_id_usuario,
            estatus_miembro=orm.estatus_miembro,
            rol_equipo=orm.rol_equipo
        )

    def create(self, equipo: Equipo) -> Equipo:
        orm_equipo = EquipoORM(
            nombre_equipo=equipo.nombre_equipo,
            fk_id_deporte=equipo.fk_id_deporte,
            fk_id_usuario_capitan=equipo.fk_id_usuario_capitan,
            url_logo_equipo=equipo.url_logo_equipo,
            descripcion_equipo=equipo.descripcion_equipo,
            esta_reclutando=equipo.esta_reclutando,
            max_miembros=equipo.max_miembros
        )
        self.db.add(orm_equipo)
        self.db.commit()
        self.db.refresh(orm_equipo)
        
        # Obtenemos el nombre del deporte para la respuesta
        deporte_orm = self.db.query(DeporteORM).filter(DeporteORM.id_deporte == equipo.fk_id_deporte).first()
        deporte = Deporte(deporte_orm.id_deporte, deporte_orm.nombre_deporte) if deporte_orm else None
        
        return self._to_entity(orm_equipo, deporte)

    def get_by_id(self, id_equipo: int) -> Optional[Equipo]:
        # Hacemos un join para traer el nombre del deporte
        result = self.db.query(EquipoORM, DeporteORM).join(
            DeporteORM, EquipoORM.fk_id_deporte == DeporteORM.id_deporte
        ).filter(EquipoORM.id_equipo == id_equipo).first()
        
        if result:
            equipo_orm, deporte_orm = result
            deporte = Deporte(deporte_orm.id_deporte, deporte_orm.nombre_deporte)
            return self._to_entity(equipo_orm, deporte)
        return None

    def add_member(self, membership: EquipoUsuario) -> EquipoUsuario:
        orm = EquipoUsuarioORM(
            fk_id_equipo=membership.fk_id_equipo,
            fk_id_usuario=membership.fk_id_usuario,
            estatus_miembro=membership.estatus_miembro,
            rol_equipo=membership.rol_equipo
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_membership_entity(orm)

    def update_member_status(self, id_equipo: int, id_usuario: int, status: str, role: str) -> bool:
        orm = self.db.query(EquipoUsuarioORM).filter(
            EquipoUsuarioORM.fk_id_equipo == id_equipo,
            EquipoUsuarioORM.fk_id_usuario == id_usuario
        ).first()
        if orm:
            orm.estatus_miembro = status
            orm.rol_equipo = role
            self.db.commit()
            return True
        return False

    def get_members(self, id_equipo: int) -> List[EquipoUsuario]:
        orms = self.db.query(EquipoUsuarioORM).filter(EquipoUsuarioORM.fk_id_equipo == id_equipo).all()
        return [self._to_membership_entity(orm) for orm in orms]

    def get_teams_by_user(self, id_usuario: int) -> List[Equipo]:
        # Busca equipos donde el usuario es miembro (aceptado) con el nombre del deporte
        results = self.db.query(EquipoORM, DeporteORM).join(
            DeporteORM, EquipoORM.fk_id_deporte == DeporteORM.id_deporte
        ).join(
            EquipoUsuarioORM, EquipoORM.id_equipo == EquipoUsuarioORM.fk_id_equipo
        ).filter(
            EquipoUsuarioORM.fk_id_usuario == id_usuario,
            EquipoUsuarioORM.estatus_miembro == 'aceptado'
        ).all()
        
        return [self._to_entity(orm, Deporte(d.id_deporte, d.nombre_deporte)) for orm, d in results]

    def delete_member(self, id_equipo: int, id_usuario: int) -> bool:
        orm = self.db.query(EquipoUsuarioORM).filter(
            EquipoUsuarioORM.fk_id_equipo == id_equipo,
            EquipoUsuarioORM.fk_id_usuario == id_usuario
        ).first()
        if orm:
            self.db.delete(orm)
            self.db.commit()
            return True
        return False

    def get_discoverable_teams(self) -> List[Equipo]:
        # Traemos equipos que estén reclutando, haciendo join para obtener el deporte
        results = self.db.query(EquipoORM, DeporteORM).join(
            DeporteORM, EquipoORM.fk_id_deporte == DeporteORM.id_deporte
        ).filter(
            EquipoORM.esta_reclutando == True
        ).all()
        
        return [self._to_entity(orm, Deporte(d.id_deporte, d.nombre_deporte)) for orm, d in results]

