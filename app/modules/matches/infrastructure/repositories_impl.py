from typing import Optional, List, cast, Any
from sqlalchemy.orm import Session
from datetime import datetime
from app.modules.matches.domain.entities import MatchEntity
from app.modules.matches.domain.interfaces import IMatchRepository
from app.modules.matches.infrastructure.orm_models import PartidaORM, PartidaUsuarioORM
from app.core.events import EventDispatcher
from app.core.specification import Specification

class MatchRepositoryImpl(IMatchRepository):
    """Implementación del repositorio de partidos con SQLAlchemy."""

    def __init__(self, db: Session):
        self.db = db

    def _dispatch_events(self, entity: MatchEntity):
        """Despacha todos los eventos acumulados en la entidad."""
        events = entity.pull_domain_events()
        for event in events:
            EventDispatcher.dispatch(event)

    def _to_entity(self, orm: PartidaORM) -> MatchEntity:
        """Convierte el modelo ORM de SQLAlchemy a la Entidad de Dominio."""
        return MatchEntity(
            id=cast(Optional[int], orm.id_partida),
            fecha_inicio_estimada=cast(datetime, orm.fecha_inicio_estimada),
            fecha_fin_estimada=cast(datetime, orm.fecha_fin_estimada),
            fecha_acordada=cast(Optional[datetime], orm.fecha_acordada),
            costo_total_partida=cast(float, orm.costo_total_partida) if orm.costo_total_partida is not None else 0.0,
            estatus_partida=cast(str, orm.estatus_partida),
            fk_id_usuario_org=cast(int, orm.fk_id_usuario_org),
            fk_id_deporte=cast(int, orm.fk_id_deporte),
            fk_id_cancha=cast(int, orm.fk_id_cancha),
            fk_id_equipo_a=cast(Optional[int], orm.fk_id_equipo_a),
            fk_id_equipo_b=cast(Optional[int], orm.fk_id_equipo_b),
            fecha_creacion_partida=cast(datetime, orm.fecha_creacion_partida),
            cupos_totales=orm.deporte.max_jugadores_deporte if getattr(orm, 'deporte', None) and orm.deporte.max_jugadores_deporte else 22,
            jugadores_inscritos=len(orm.participantes) if hasattr(orm, 'participantes') else 0,
            propuesta_fecha_a=cast(Optional[datetime], orm.propuesta_fecha_a),
            propuesta_costo_a=cast(Optional[float], orm.propuesta_costo_a),
            propuesta_fecha_b=cast(Optional[datetime], orm.propuesta_fecha_b),
            propuesta_costo_b=cast(Optional[float], orm.propuesta_costo_b),
            equipo_a_listo=cast(bool, orm.equipo_a_listo),
            equipo_b_listo=cast(bool, orm.equipo_b_listo),
            resultado_goles_a_cap_a=cast(Optional[int], orm.resultado_goles_a_cap_a),
            resultado_goles_b_cap_a=cast(Optional[int], orm.resultado_goles_b_cap_a),
            resultado_goles_a_cap_b=cast(Optional[int], orm.resultado_goles_a_cap_b),
            resultado_goles_b_cap_b=cast(Optional[int], orm.resultado_goles_b_cap_b),
            
            # Campos enriquecidos vía relaciones
            nombre_equipo_a=orm.equipo_a.nombre_equipo if orm.equipo_a else None,
            logo_equipo_a=orm.equipo_a.url_logo_equipo if orm.equipo_a else None,
            nombre_capitan_a=orm.organizador.nombre_usuario if orm.organizador else None,
            nombre_cancha=orm.cancha.nombre_cancha if orm.cancha else None,
            nombre_deporte=orm.deporte.nombre_deporte if orm.deporte else None,
            id_capitan_b=orm.equipo_b.fk_id_usuario_capitan if orm.equipo_b else None,
            nombre_equipo_b=orm.equipo_b.nombre_equipo if orm.equipo_b else None,
            logo_equipo_b=orm.equipo_b.url_logo_equipo if orm.equipo_b else None,
            telefono_capitan_a=orm.organizador.telefono_usuario if orm.organizador else None,
            telefono_capitan_b=orm.equipo_b.capitan.telefono_usuario if (orm.equipo_b and orm.equipo_b.capitan) else None,
            latitud_cancha=orm.cancha.latitud_cancha if orm.cancha else None,
            longitud_cancha=orm.cancha.longitud_cancha if orm.cancha else None,
            banco_receptor=orm.organizador.datos_bancarios.banco if (orm.organizador and orm.organizador.datos_bancarios) else None,
            cedula_receptora=orm.organizador.datos_bancarios.cedula if (orm.organizador and orm.organizador.datos_bancarios) else None,
            telefono_receptor=orm.organizador.datos_bancarios.telefono if (orm.organizador and orm.organizador.datos_bancarios) else None,
            banco_capitan_b=orm.equipo_b.capitan.datos_bancarios.banco if (orm.equipo_b and orm.equipo_b.capitan and orm.equipo_b.capitan.datos_bancarios) else None,
            cedula_capitan_b=orm.equipo_b.capitan.datos_bancarios.cedula if (orm.equipo_b and orm.equipo_b.capitan and orm.equipo_b.capitan.datos_bancarios) else None,
            telefono_capitan_b_pago=orm.equipo_b.capitan.datos_bancarios.telefono if (orm.equipo_b and orm.equipo_b.capitan and orm.equipo_b.capitan.datos_bancarios) else None
        )

    def create(self, match: MatchEntity) -> MatchEntity:
        orm = PartidaORM(
            fecha_inicio_estimada=match.fecha_inicio_estimada,
            fecha_fin_estimada=match.fecha_fin_estimada,
            costo_total_partida=match.costo_total_partida,
            fk_id_usuario_org=match.fk_id_usuario_org,
            fk_id_deporte=match.fk_id_deporte,
            fk_id_cancha=match.fk_id_cancha,
            fk_id_equipo_a=match.fk_id_equipo_a,
            fk_id_equipo_b=match.fk_id_equipo_b,
            estatus_partida=match.estatus_partida
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        entity = self._to_entity(orm)
        
        # Si tiene equipos, podemos disparar los eventos manualmente si la entidad no los capturó
        # (Ya que al crear desde cero vía ORM la entidad aún no existe)
        from app.modules.matches.domain.events import TeamAssignedToMatch
        fk_a = cast(Optional[int], orm.fk_id_equipo_a)
        fk_b = cast(Optional[int], orm.fk_id_equipo_b)
        if fk_a is not None:
            self._register_team_members(cast(int, orm.id_partida), fk_a)
            EventDispatcher.dispatch(TeamAssignedToMatch(match_id=cast(int, orm.id_partida), team_id=fk_a))
        if fk_b is not None:
            self._register_team_members(cast(int, orm.id_partida), fk_b)
            EventDispatcher.dispatch(TeamAssignedToMatch(match_id=cast(int, orm.id_partida), team_id=fk_b))

        return entity

    def get_by_id(self, match_id: int) -> Optional[MatchEntity]:
        from sqlalchemy.orm import joinedload
        from app.modules.teams.infrastructure.orm_models import EquipoORM
        from app.modules.users.infrastructure.orm_models import UsuarioORM
        orm = self.db.query(PartidaORM).options(
            joinedload(PartidaORM.organizador).joinedload(UsuarioORM.datos_bancarios),
            joinedload(PartidaORM.deporte),
            joinedload(PartidaORM.cancha),
            joinedload(PartidaORM.equipo_a),
            joinedload(PartidaORM.equipo_b).joinedload(EquipoORM.capitan)
        ).filter(PartidaORM.id_partida == match_id).first()
        
        return self._to_entity(orm) if orm else None

    def find(self, specification: Specification) -> List[MatchEntity]:
        from app.modules.teams.infrastructure.orm_models import EquipoORM
        from app.modules.users.infrastructure.orm_models import UsuarioORM
        from sqlalchemy.orm import joinedload
        
        query = self.db.query(PartidaORM).options(
            joinedload(PartidaORM.organizador).joinedload(UsuarioORM.datos_bancarios),
            joinedload(PartidaORM.deporte),
            joinedload(PartidaORM.cancha),
            joinedload(PartidaORM.equipo_a),
            joinedload(PartidaORM.equipo_b).joinedload(EquipoORM.capitan)
        )
        
        query = cast(Any, specification.apply_to_query(query, PartidaORM))
        results = query.all()
        return [self._to_entity(orm) for orm in results]

    def get_all(self, 
                sport_id: Optional[int] = None, 
                status: Optional[str] = None,
                region_id: Optional[int] = None,
                cancha_id: Optional[int] = None,
                fecha: Optional[datetime] = None,
                user_id: Optional[int] = None,
                team_id: Optional[int] = None,
                exclude_user_id: Optional[int] = None) -> List[MatchEntity]:
        from app.modules.matches.domain.specifications import (
            MatchBySport, MatchByStatus, MatchByCancha, MatchByDate, MatchByUserInvolved, ExcludeMatchesByUserTeams
        )
        
        specs = []
        if sport_id: specs.append(MatchBySport(sport_id))
        if status: specs.append(MatchByStatus(status))
        if cancha_id: specs.append(MatchByCancha(cancha_id))
        if fecha: specs.append(MatchByDate(fecha))
        if user_id: specs.append(MatchByUserInvolved(user_id))
        if exclude_user_id: specs.append(ExcludeMatchesByUserTeams(exclude_user_id))
        if team_id:
            from app.modules.matches.domain.specifications import MatchByTeamInvolved
            specs.append(MatchByTeamInvolved(team_id))
        
        if not specs:
            # Si no hay filtros, creamos una especificación que siempre sea verdadera o simplemente buscamos todos
            from sqlalchemy.orm import joinedload
            from app.modules.teams.infrastructure.orm_models import EquipoORM
            from app.modules.users.infrastructure.orm_models import UsuarioORM
            results = self.db.query(PartidaORM).options(
                joinedload(PartidaORM.organizador).joinedload(UsuarioORM.datos_bancarios),
                joinedload(PartidaORM.deporte),
                joinedload(PartidaORM.cancha),
                joinedload(PartidaORM.equipo_a),
                joinedload(PartidaORM.equipo_b).joinedload(EquipoORM.capitan)
            ).all()
            return [self._to_entity(orm) for orm in results]

        # Combinar todas las especificaciones con AND
        composite_spec = specs[0]
        for next_spec in specs[1:]:
            composite_spec = composite_spec & next_spec
            
        return self.find(composite_spec)

    def update(self, match_id: int, data: dict) -> Optional[MatchEntity]:
        orm = self.db.query(PartidaORM).filter(PartidaORM.id_partida == match_id).first()
        if not orm:
            return None
        
        # Guardar estados previos para detectar cambios de equipo
        old_equipo_a = cast(Optional[int], orm.fk_id_equipo_a)
        old_equipo_b = cast(Optional[int], orm.fk_id_equipo_b)

        for key, value in data.items():
            if hasattr(orm, key):
                setattr(orm, key, value)
        
        self.db.commit()

        # Convertir a entidad y disparar eventos registrados en ella
        entity = self.get_by_id(match_id)
        if entity:
            # Detectar cambios de equipo y registrar eventos si no se hizo en la capa superior
            # (En un sistema ideal, esto se haría en el UseCase llamando a entity.assign_team_x)
            from app.modules.matches.domain.events import TeamAssignedToMatch
            fk_a = cast(Optional[int], orm.fk_id_equipo_a)
            fk_b = cast(Optional[int], orm.fk_id_equipo_b)
            if fk_a is not None and fk_a != old_equipo_a:
                self._register_team_members(match_id, fk_a)
                EventDispatcher.dispatch(TeamAssignedToMatch(match_id=match_id, team_id=fk_a))
            if fk_b is not None and fk_b != old_equipo_b:
                self._register_team_members(match_id, fk_b)
                EventDispatcher.dispatch(TeamAssignedToMatch(match_id=match_id, team_id=fk_b))
            
            self._dispatch_events(entity)

        return entity

    def _register_team_members(self, match_id: int, team_id: int):
        """Registra a todos los miembros aceptados de un equipo en la partida."""
        from app.modules.teams.infrastructure.orm_models import EquipoUsuarioORM
        
        members = self.db.query(EquipoUsuarioORM).filter(
            EquipoUsuarioORM.fk_id_equipo == team_id,
            EquipoUsuarioORM.estatus_miembro == 'aceptado'
        ).all()
        
        for m in members:
            # Evitar duplicados
            exists = self.db.query(PartidaUsuarioORM).filter(
                PartidaUsuarioORM.fk_id_partida == match_id,
                PartidaUsuarioORM.fk_id_usuario == m.fk_id_usuario
            ).first()
            
            if not exists:
                pu = PartidaUsuarioORM(
                    fk_id_partida=match_id,
                    fk_id_usuario=m.fk_id_usuario,
                    fk_id_equipo_asignado=team_id
                )
                self.db.add(pu)
        
        self.db.commit()

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
        from app.modules.users.infrastructure.orm_models import UsuarioORM
        
        results = self.db.query(
            PartidaUsuarioORM, 
            UsuarioORM.nombre_usuario, 
            UsuarioORM.url_foto_perfil
        ).join(
            UsuarioORM, 
            PartidaUsuarioORM.fk_id_usuario == UsuarioORM.id_usuario
        ).filter(
            PartidaUsuarioORM.fk_id_partida == match_id
        ).all()
        
        return [
            {
                "id_usuario": r[0].fk_id_usuario,
                "nombre_usuario": r.nombre_usuario,
                "url_foto_perfil": r.url_foto_perfil,
                "estatus_pago": r[0].estatus_pago,
                "url_recibo_pago": r[0].url_recibo_pago,
                "referencia_pago": r[0].referencia_pago,
                "id_equipo": r[0].fk_id_equipo_asignado
            } for r in results
        ]

    def update_terms(self, match_id: int, user_id: int, is_captain_a: bool, fecha: datetime, costo: float) -> Optional[MatchEntity]:
        orm = self.db.query(PartidaORM).filter(PartidaORM.id_partida == match_id).first()
        if not orm:
            return None
        if is_captain_a:
            setattr(orm, "propuesta_fecha_a", fecha)
            setattr(orm, "propuesta_costo_a", costo)
        else:
            setattr(orm, "propuesta_fecha_b", fecha)
            setattr(orm, "propuesta_costo_b", costo)
        
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def configure_match(self, match_id: int, user_id: int, fecha: datetime, costo: float, banco: str, cedula: str, telefono: str) -> Optional[MatchEntity]:
        from app.modules.users.infrastructure.orm_models import DatosBancariosORM
        from app.modules.teams.infrastructure.orm_models import EquipoORM
        
        orm = self.db.query(PartidaORM).filter(PartidaORM.id_partida == match_id).first()
        if not orm:
            return None
        
        # Identificar roles
        organizador_id = cast(int, orm.fk_id_usuario_org)
        fk_b = cast(Optional[int], orm.fk_id_equipo_b)
        is_capitan_a = organizador_id == user_id
        
        # Verificar si es capitán del equipo B
        equipo_b = self.db.query(EquipoORM).filter(EquipoORM.id_equipo == fk_b).first() if fk_b is not None else None
        is_capitan_b = bool(equipo_b and equipo_b.fk_id_usuario_capitan == user_id)

        if is_capitan_a:
            setattr(orm, "propuesta_fecha_a", fecha)
            setattr(orm, "propuesta_costo_a", costo)
        elif is_capitan_b:
            setattr(orm, "propuesta_fecha_b", fecha)
            setattr(orm, "propuesta_costo_b", costo)
        # Verificar acuerdo mutuo para cambiar a pendiente_pago
        propuesta_fecha_a = cast(Optional[datetime], orm.propuesta_fecha_a)
        propuesta_fecha_b = cast(Optional[datetime], orm.propuesta_fecha_b)
        propuesta_costo_a = cast(Optional[float], orm.propuesta_costo_a)
        propuesta_costo_b = cast(Optional[float], orm.propuesta_costo_b)

        if propuesta_fecha_a is not None and propuesta_fecha_b is not None and \
           propuesta_costo_a is not None and propuesta_costo_b is not None and \
           propuesta_costo_a == propuesta_costo_b and \
           propuesta_fecha_a == propuesta_fecha_b:
            setattr(orm, "fecha_acordada", propuesta_fecha_a)
            setattr(orm, "costo_total_partida", propuesta_costo_a)
            setattr(orm, "estatus_partida", 'pendiente_pago')
            
            # Auto-verificar pago de ambos capitanes
            cap_a_id = orm.fk_id_usuario_org
            cap_b_id = equipo_b.fk_id_usuario_capitan if equipo_b else None
            
            self.db.query(PartidaUsuarioORM).filter(
                PartidaUsuarioORM.fk_id_partida == match_id,
                PartidaUsuarioORM.fk_id_usuario.in_([cap_a_id, cap_b_id] if cap_b_id else [cap_a_id])
            ).update({"estatus_pago": "verificado"}, synchronize_session=False)
            
        # Actualizar datos bancarios del usuario que configura
        datos_orm = self.db.query(DatosBancariosORM).filter(DatosBancariosORM.fk_id_usuario == user_id).first()
        if datos_orm:
            setattr(datos_orm, "banco", banco)
            setattr(datos_orm, "cedula", cedula)
            setattr(datos_orm, "telefono", telefono)
        else:
            datos_orm = DatosBancariosORM(
                fk_id_usuario=user_id,
                banco=banco,
                cedula=cedula,
                telefono=telefono
            )
            self.db.add(datos_orm)
            
        self.db.commit()
        return self.get_by_id(match_id)

    def mark_team_ready(self, match_id: int, team_id: int) -> Optional[MatchEntity]:
        orm = self.db.query(PartidaORM).filter(PartidaORM.id_partida == match_id).first()
        if not orm:
            return None

        fk_a = cast(Optional[int], orm.fk_id_equipo_a)
        fk_b = cast(Optional[int], orm.fk_id_equipo_b)
        if fk_a == team_id:
            setattr(orm, "equipo_a_listo", True)
        elif fk_b == team_id:
            setattr(orm, "equipo_b_listo", True)
            
        equipo_a_listo = cast(bool, orm.equipo_a_listo)
        equipo_b_listo = cast(bool, orm.equipo_b_listo)
        if equipo_a_listo and equipo_b_listo:
            setattr(orm, "estatus_partida", "confirmada")
            
        self.db.commit()
        return self.get_by_id(match_id)

    def submit_result_proposal(self, match_id: int, user_id: int, goals_a: int, goals_b: int) -> Optional[MatchEntity]:
        orm = self.db.query(PartidaORM).filter(PartidaORM.id_partida == match_id).first()
        if not orm:
            return None
        organizador_id = cast(int, orm.fk_id_usuario_org)
        if organizador_id == user_id:
            # Es el capitán A
            setattr(orm, "resultado_goles_a_cap_a", goals_a)
            setattr(orm, "resultado_goles_b_cap_a", goals_b)
        else:
            # Es el capitán B
            setattr(orm, "resultado_goles_a_cap_b", goals_a)
            setattr(orm, "resultado_goles_b_cap_b", goals_b)
            
        self.db.commit()

        # Verificar si coinciden para auto-completar
        g_a_a = cast(Optional[int], orm.resultado_goles_a_cap_a)
        g_b_a = cast(Optional[int], orm.resultado_goles_b_cap_a)
        g_a_b = cast(Optional[int], orm.resultado_goles_a_cap_b)
        g_b_b = cast(Optional[int], orm.resultado_goles_b_cap_b)

        if g_a_a is not None and g_b_a is not None and g_a_b is not None and g_b_b is not None:
            if g_a_a == g_a_b and g_b_a == g_b_b:
                # EVITAR DUPLICADOS: Solo procesar si la partida no ha sido completada ya
                if orm.estatus_partida != 'completada':
                    fk_a = cast(int, orm.fk_id_equipo_a)
                    fk_b = cast(int, orm.fk_id_equipo_b)
                    self.register_result(match_id, fk_a, fk_b, g_a_a, g_b_a)

        return self.get_by_id(match_id)

    def register_result(self, match_id: int, team_a_id: int, team_b_id: int, goals_a: int, goals_b: int) -> None:
        from app.modules.matches.infrastructure.orm_models import ResultadoORM
        
        # Puntos
        pts_a, pts_b = 1, 1
        txt_a, txt_b = "Empate", "Empate"
        if goals_a > goals_b:
            pts_a, txt_a = 3, "Victoria"
            pts_b, txt_b = 0, "Derrota"
        elif goals_b > goals_a:
            pts_a, txt_a = 0, "Derrota"
            pts_b, txt_b = 3, "Victoria"
            
        res_a = ResultadoORM(
            fk_id_partida=match_id, fk_id_equipo=team_a_id,
            goles_favor=goals_a, goles_contra=goals_b,
            puntos_obtenidos=pts_a, resultado_texto=txt_a
        )
        res_b = ResultadoORM(
            fk_id_partida=match_id, fk_id_equipo=team_b_id,
            goles_favor=goals_b, goles_contra=goals_a,
            puntos_obtenidos=pts_b, resultado_texto=txt_b
        )
        
        self.db.add_all([res_a, res_b])
        
        # Marcar partida completada
        orm = self.db.query(PartidaORM).filter(PartidaORM.id_partida == match_id).first()
        if orm:
            setattr(orm, "estatus_partida", "completada")
            
        self.db.commit()

    def delete(self, match_id: int) -> bool:
        from app.modules.matches.infrastructure.orm_models import PartidaUsuarioORM
        # Eliminar registros relacionados en PartidaUsuario primero
        self.db.query(PartidaUsuarioORM).filter(PartidaUsuarioORM.fk_id_partida == match_id).delete()
        
        # Eliminar el partido
        orm = self.db.query(PartidaORM).filter(PartidaORM.id_partida == match_id).first()
        if orm:
            self.db.delete(orm)
            self.db.commit()
            return True
        return False
