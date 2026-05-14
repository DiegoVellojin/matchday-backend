from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict

from app.modules.rankings.domain.interfaces import IRankingRepository

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
