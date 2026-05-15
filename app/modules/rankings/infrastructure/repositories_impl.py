from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Optional
from app.modules.rankings.domain.interfaces import IRankingRepository
from app.modules.rankings.infrastructure.orm_models import EvaluacionORM
from app.modules.matches.infrastructure.orm_models import PartidaORM
from app.modules.teams.infrastructure.orm_models import EquipoORM
from app.modules.users.infrastructure.orm_models import UsuarioORM

class RankingRepositoryImpl(IRankingRepository):
    """Implementación del repositorio de Rankings."""
    def __init__(self, db: Session):
        self.db = db

    def get_team_leaderboard(self, sport_id: int | None = None) -> List[Dict]:
        # Filtro opcional por deporte
        where_clause = ""
        params = {}
        if sport_id:
            where_clause = "WHERE e.fk_id_deporte = :sport_id"
            params["sport_id"] = sport_id

        # Calculamos el leaderboard dinámicamente sumando puntos en Resultado
        query = f"""
        SELECT 
            e.id_equipo,
            e.nombre_equipo,
            e.url_logo_equipo,
            d.nombre_deporte,
            COALESCE(SUM(r.puntos_obtenidos), 0) as puntos_totales,
            COUNT(r.id_resultado) as partidos_jugados,
            COALESCE(SUM(CASE WHEN r.resultado_texto = 'Victoria' THEN 1 ELSE 0 END), 0) as victorias,
            COALESCE(SUM(CASE WHEN r.resultado_texto = 'Empate' THEN 1 ELSE 0 END), 0) as empates,
            COALESCE(SUM(CASE WHEN r.resultado_texto = 'Derrota' THEN 1 ELSE 0 END), 0) as derrotas
        FROM bd_matchday."Equipo" e
        JOIN bd_matchday."Deporte" d ON e.fk_id_deporte = d.id_deporte
        LEFT JOIN bd_matchday."Resultado" r ON e.id_equipo = r.fk_id_equipo
        {where_clause}
        GROUP BY e.id_equipo, e.nombre_equipo, e.url_logo_equipo, d.nombre_deporte
        ORDER BY puntos_totales DESC, victorias DESC, partidos_jugados ASC
        """
        result = self.db.execute(text(query), params).fetchall()
        
        leaderboard = []
        for i, row in enumerate(result):
            leaderboard.append({
                "posicion": i + 1,
                "id_equipo": row.id_equipo,
                "nombre_equipo": row.nombre_equipo,
                "url_logo_equipo": row.url_logo_equipo,
                "deporte": row.nombre_deporte,
                "puntos_totales": int(row.puntos_totales),
                "partidos_jugados": int(row.partidos_jugados),
                "victorias": int(row.victorias),
                "empates": int(row.empates),
                "derrotas": int(row.derrotas)
            })
            
        return leaderboard

    def has_evaluated(self, partida_id: int, evaluador_id: int) -> bool:
        return self.db.query(EvaluacionORM).filter(
            EvaluacionORM.fk_id_partida == partida_id,
            EvaluacionORM.fk_id_evaluador == evaluador_id
        ).first() is not None

    def evaluate_team(self, partida_id: int, evaluador_id: int, puntuacion: int, comentario: str | None = None) -> bool:
        # 1. Obtener la partida para identificar al equipo rival y su capitán
        partida = self.db.query(PartidaORM).filter(PartidaORM.id_partida == partida_id).first()
        if not partida:
            return False

        # Identificar quién es el evaluado
        if evaluador_id == partida.fk_id_usuario_org:
            # El evaluador es el capitán A, el evaluado es el equipo B y su capitán
            # Necesitamos encontrar al capitán B. El capitán B es quien aceptó el partido.
            # En PartidaORM no tenemos id_usuario_rival directamente, pero podemos inferirlo de equipo_b
            evaluado_equipo_id = partida.fk_id_equipo_b
            if not evaluado_equipo_id: return False
            equipo_b = self.db.query(EquipoORM).filter(EquipoORM.id_equipo == evaluado_equipo_id).first()
            evaluado_capitan_id = equipo_b.fk_id_usuario_capitan
        else:
            # El evaluador es el capitán B, el evaluado es el equipo A y su capitán
            evaluado_equipo_id = partida.fk_id_equipo_a
            evaluado_capitan_id = partida.fk_id_usuario_org

        if not evaluado_equipo_id or not evaluado_capitan_id:
            return False

        # 2. Registrar la evaluación
        nueva_evaluacion = EvaluacionORM(
            fk_id_partida=partida_id,
            fk_id_evaluador=evaluador_id,
            fk_id_evaluado_equipo=evaluado_equipo_id,
            fk_id_evaluado_capitan=evaluado_capitan_id,
            puntuacion=puntuacion,
            comentario=comentario
        )
        self.db.add(nueva_evaluacion)

        # 3. Actualizar promedio del equipo
        equipo = self.db.query(EquipoORM).filter(EquipoORM.id_equipo == evaluado_equipo_id).first()
        if equipo:
            total_estrellas = (equipo.calificacion_promedio * equipo.num_calificaciones) + puntuacion
            equipo.num_calificaciones += 1
            equipo.calificacion_promedio = total_estrellas / equipo.num_calificaciones

        # 4. Actualizar promedio del capitán (reliability_score)
        capitan = self.db.query(UsuarioORM).filter(UsuarioORM.id_usuario == evaluado_capitan_id).first()
        if capitan:
            total_estrellas_cap = (capitan.reliability_score * capitan.num_calificaciones_capitan) + puntuacion
            capitan.num_calificaciones_capitan += 1
            capitan.reliability_score = total_estrellas_cap / capitan.num_calificaciones_capitan

        self.db.commit()
        return True

    def get_evaluations(self, target_id: int, is_team: bool) -> List[Dict]:
        query = self.db.query(EvaluacionORM)
        if is_team:
            query = query.filter(EvaluacionORM.fk_id_evaluado_equipo == target_id)
        else:
            query = query.filter(EvaluacionORM.fk_id_evaluado_capitan == target_id)
        
        evaluaciones = query.order_by(EvaluacionORM.fecha_evaluacion.desc()).all()
        
        result = []
        for e in evaluaciones:
            # Para cada evaluación, necesitamos saber quién evaluó (Capitán) y de qué equipo era
            # El evaluador es e.evaluador. El equipo del evaluador es el equipo_a o equipo_b de la partida 
            # que NO es el equipo evaluado.
            partida = e.partida
            if not partida: continue
            
            # Determinar el equipo del evaluador
            if e.fk_id_evaluador == partida.fk_id_usuario_org:
                equipo_evaluador = partida.equipo_a
            else:
                equipo_evaluador = partida.equipo_b
                
            result.append({
                "id_evaluacion": e.id_evaluacion,
                "puntuacion": e.puntuacion,
                "comentario": e.comentario,
                "fecha": e.fecha_evaluacion,
                "evaluador": {
                    "nombre": e.evaluador.nombre_usuario if e.evaluador else "Usuario",
                    "foto": e.evaluador.url_foto_perfil if e.evaluador else None
                },
                "equipo_evaluador": {
                    "nombre": equipo_evaluador.nombre_equipo if equipo_evaluador else "Equipo",
                    "logo": equipo_evaluador.url_logo_equipo if equipo_evaluador else None
                }
            })
        return result
