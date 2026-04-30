from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from app.modules.matches.domain.entities import MatchEntity
from app.modules.matches.domain.interfaces import IMatchRepository
from app.modules.matches.infrastructure.orm_models import PartidaORM, PartidaUsuarioORM

class MatchRepositoryImpl(IMatchRepository):
    """Implementación del repositorio de partidos con SQLAlchemy."""

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, orm: PartidaORM) -> MatchEntity:
        return MatchEntity(
            id=orm.id_partida,
            fecha_inicio_estimada=orm.fecha_inicio_estimada,
            fecha_fin_estimada=orm.fecha_fin_estimada,
            fecha_acordada=orm.fecha_acordada,
            costo_total_partida=float(orm.costo_total_partida),
            estatus_partida=orm.estatus_partida,
            fk_id_usuario_org=orm.fk_id_usuario_org,
            fk_id_deporte=orm.fk_id_deporte,
            fk_id_cancha=orm.fk_id_cancha,
            fk_id_equipo_a=orm.fk_id_equipo_a,
            fk_id_equipo_b=orm.fk_id_equipo_b,
            fecha_creacion_partida=orm.fecha_creacion_partida,
            propuesta_fecha_a=orm.propuesta_fecha_a,
            propuesta_costo_a=float(orm.propuesta_costo_a) if orm.propuesta_costo_a else None,
            propuesta_fecha_b=orm.propuesta_fecha_b,
            propuesta_costo_b=float(orm.propuesta_costo_b) if orm.propuesta_costo_b else None,
        )

    def create(self, match: MatchEntity) -> MatchEntity:
        orm = PartidaORM(
            fecha_inicio_estimada=match.fecha_inicio_estimada,
            fecha_fin_estimada=match.fecha_fin_estimada,
            fk_id_usuario_org=match.fk_id_usuario_org,
            fk_id_deporte=match.fk_id_deporte,
            fk_id_cancha=match.fk_id_cancha,
            fk_id_equipo_a=match.fk_id_equipo_a,
            estatus_partida=match.estatus_partida
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def get_by_id(self, match_id: int) -> Optional[MatchEntity]:
        from app.modules.teams.infrastructure.orm_models import EquipoORM
        from app.modules.catalogs.infrastructure.orm_models import CanchaORM, DeporteORM
        from app.modules.users.infrastructure.orm_models import UsuarioORM

        result = self.db.query(
            PartidaORM, 
            EquipoORM.nombre_equipo, 
            EquipoORM.url_logo_equipo,
            UsuarioORM.nombre_usuario,
            CanchaORM.nombre_cancha,
            DeporteORM.nombre_deporte
        ).join(
            UsuarioORM, PartidaORM.fk_id_usuario_org == UsuarioORM.id_usuario
        ).join(
            CanchaORM, PartidaORM.fk_id_cancha == CanchaORM.id_cancha
        ).join(
            DeporteORM, PartidaORM.fk_id_deporte == DeporteORM.id_deporte
        ).outerjoin(
            EquipoORM, PartidaORM.fk_id_equipo_a == EquipoORM.id_equipo
        ).filter(PartidaORM.id_partida == match_id).first()
        
        if not result:
            return None
            
        orm, team_name, team_logo, user_name, court_name, sport_name = result
        entity = self._to_entity(orm)
        entity.nombre_equipo_a = team_name
        entity.logo_equipo_a = team_logo
        entity.nombre_capitan_a = user_name
        entity.nombre_cancha = court_name
        entity.nombre_deporte = sport_name
        return entity

    def get_all(self, 
                sport_id: Optional[int] = None, 
                status: Optional[str] = None,
                region_id: Optional[int] = None,
                cancha_id: Optional[int] = None,
                fecha: Optional[datetime] = None) -> List[MatchEntity]:
        from app.modules.teams.infrastructure.orm_models import EquipoORM
        from app.modules.catalogs.infrastructure.orm_models import CanchaORM, DeporteORM
        from app.modules.users.infrastructure.orm_models import UsuarioORM
        from sqlalchemy import func
        query = self.db.query(
            PartidaORM, 
            EquipoORM.nombre_equipo, 
            EquipoORM.url_logo_equipo,
            UsuarioORM.nombre_usuario,
            CanchaORM.nombre_cancha,
            DeporteORM.nombre_deporte
        ).join(
            UsuarioORM, PartidaORM.fk_id_usuario_org == UsuarioORM.id_usuario
        ).join(
            CanchaORM, PartidaORM.fk_id_cancha == CanchaORM.id_cancha
        ).join(
            DeporteORM, PartidaORM.fk_id_deporte == DeporteORM.id_deporte
        ).outerjoin(
            EquipoORM, PartidaORM.fk_id_equipo_a == EquipoORM.id_equipo
        )

        if sport_id:
            query = query.filter(PartidaORM.fk_id_deporte == sport_id)
        if status:
            query = query.filter(PartidaORM.estatus_partida == status)
        if region_id:
            query = query.filter(CanchaORM.fk_id_region == region_id)
        if cancha_id:
            query = query.filter(PartidaORM.fk_id_cancha == cancha_id)
        if fecha:
            query = query.filter(func.date(PartidaORM.fecha_inicio_estimada) == fecha.date())
        
        results = query.all()
        
        entities = []
        for orm, team_name, team_logo, user_name, court_name, sport_name in results:
            entity = self._to_entity(orm)
            entity.nombre_equipo_a = team_name
            entity.logo_equipo_a = team_logo
            entity.nombre_capitan_a = user_name
            entity.nombre_cancha = court_name
            entity.nombre_deporte = sport_name
            entities.append(entity)
            
        return entities

    def update(self, match_id: int, data: dict) -> Optional[MatchEntity]:
        orm = self.db.query(PartidaORM).filter(PartidaORM.id_partida == match_id).first()
        if not orm:
            return None
        
        for key, value in data.items():
            if hasattr(orm, key):
                setattr(orm, key, value)
        
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def add_player(self, match_id: int, user_id: int, team_id: Optional[int] = None) -> bool:
        orm = PartidaUsuarioORM(
            fk_id_partida=match_id,
            fk_id_usuario=user_id,
            fk_id_equipo_asignado=team_id
        )
        self.db.add(orm)
        self.db.commit()
        return True

    def get_players(self, match_id: int) -> List[dict]:
        results = self.db.query(PartidaUsuarioORM).filter(PartidaUsuarioORM.fk_id_partida == match_id).all()
        return [
            {
                "id_usuario": r.fk_id_usuario,
                "estatus_pago": r.estatus_pago,
                "id_equipo": r.fk_id_equipo_asignado
            } for r in results
        ]

    def update_terms(self, match_id: int, user_id: int, is_captain_a: bool, fecha: datetime, costo: float) -> MatchEntity:
        orm = self.db.query(PartidaORM).filter(PartidaORM.id_partida == match_id).first()
        if is_captain_a:
            orm.propuesta_fecha_a = fecha
            orm.propuesta_costo_a = costo
        else:
            orm.propuesta_fecha_b = fecha
            orm.propuesta_costo_b = costo
        
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)
