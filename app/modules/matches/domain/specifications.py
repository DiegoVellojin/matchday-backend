from datetime import datetime
from typing import Optional
from app.core.specification import Specification
from app.modules.matches.infrastructure.orm_models import PartidaORM
from sqlalchemy import func, or_

class MatchBySport(Specification):
    def __init__(self, sport_id: int):
        self.sport_id = sport_id

    def is_satisfied_by(self, match) -> bool:
        return match.fk_id_deporte == self.sport_id

    def apply_to_query(self, query, model):
        return query.filter(model.fk_id_deporte == self.sport_id)

class MatchByStatus(Specification):
    def __init__(self, status: str):
        self.status = status

    def is_satisfied_by(self, match) -> bool:
        return match.estatus_partida == self.status

    def apply_to_query(self, query, model):
        return query.filter(model.estatus_partida == self.status)

class MatchByCancha(Specification):
    def __init__(self, cancha_id: int):
        self.cancha_id = cancha_id

    def is_satisfied_by(self, match) -> bool:
        return match.fk_id_cancha == self.cancha_id

    def apply_to_query(self, query, model):
        return query.filter(model.fk_id_cancha == self.cancha_id)

class MatchByDate(Specification):
    def __init__(self, date: datetime):
        self.date = date

    def is_satisfied_by(self, match) -> bool:
        return match.fecha_inicio_estimada.date() == self.date.date()

    def apply_to_query(self, query, model):
        return query.filter(func.date(model.fecha_inicio_estimada) == self.date.date())

class MatchByUserInvolved(Specification):
    """Filtra partidos donde el usuario está involucrado (Organizador, Jugador o Capitán)."""
    def __init__(self, user_id: int):
        self.user_id = user_id

    def is_satisfied_by(self, match) -> bool:
        # Implementación simplificada en memoria
        return match.fk_id_usuario_org == self.user_id

    def apply_to_query(self, query, model):
        from app.modules.matches.infrastructure.orm_models import PartidaUsuarioORM
        from app.modules.teams.infrastructure.orm_models import EquipoUsuarioORM
        from app.modules.teams.infrastructure.orm_models import EquipoORM
        from sqlalchemy.orm import aliased
        from sqlalchemy import select, or_
        
        EqA = aliased(EquipoORM)
        EqB = aliased(EquipoORM)
        
        # Equipos donde el usuario es miembro aceptado
        subq_user_teams = select(EquipoUsuarioORM.fk_id_equipo).where(
            EquipoUsuarioORM.fk_id_usuario == self.user_id,
            EquipoUsuarioORM.estatus_miembro == 'aceptado'
        )
        
        query = query.outerjoin(PartidaUsuarioORM, model.id_partida == PartidaUsuarioORM.fk_id_partida)
        query = query.outerjoin(EqA, model.fk_id_equipo_a == EqA.id_equipo)
        query = query.outerjoin(EqB, model.fk_id_equipo_b == EqB.id_equipo)
        
        return query.filter(or_(
            model.fk_id_usuario_org == self.user_id,
            PartidaUsuarioORM.fk_id_usuario == self.user_id,
            EqA.fk_id_usuario_capitan == self.user_id,
            EqB.fk_id_usuario_capitan == self.user_id,
            model.fk_id_equipo_a.in_(subq_user_teams),
            model.fk_id_equipo_b.in_(subq_user_teams)
        )).distinct()

class ExcludeMatchesByUserTeams(Specification):
    """Excluye partidos donde el usuario o alguno de sus equipos está involucrado."""
    def __init__(self, user_id: int):
        self.user_id = user_id

    def is_satisfied_by(self, match) -> bool:
        # Simplificado para evaluación en memoria si fuese necesario
        return match.fk_id_usuario_org != self.user_id

    def apply_to_query(self, query, model):
        from app.modules.teams.infrastructure.orm_models import EquipoUsuarioORM
        from sqlalchemy import select

        # Equipos donde el usuario es miembro aceptado
        subq_user_teams = select(EquipoUsuarioORM.fk_id_equipo).where(
            EquipoUsuarioORM.fk_id_usuario == self.user_id,
            EquipoUsuarioORM.estatus_miembro == 'aceptado'
        )

        return query.filter(
            model.fk_id_usuario_org != self.user_id,
            (model.fk_id_equipo_a.is_(None)) | (~model.fk_id_equipo_a.in_(subq_user_teams)),
            (model.fk_id_equipo_b.is_(None)) | (~model.fk_id_equipo_b.in_(subq_user_teams))
        )

class MatchByTeamInvolved(Specification):
    def __init__(self, team_id: int):
        self.team_id = team_id

    def is_satisfied_by(self, match) -> bool:
        return match.fk_id_equipo_a == self.team_id or match.fk_id_equipo_b == self.team_id

    def apply_to_query(self, query, model):
        return query.filter(or_(
            model.fk_id_equipo_a == self.team_id,
            model.fk_id_equipo_b == self.team_id
        ))
