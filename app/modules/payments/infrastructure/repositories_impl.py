from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Optional

from app.modules.payments.domain.interfaces import IPaymentRepository

class PaymentRepositoryImpl(IPaymentRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_user_payments(self, user_id: int) -> List[Dict]:
        query = """
        SELECT 
            p.id_partida,
            e.nombre_equipo,
            e.url_logo_equipo,
            p.fecha_inicio_estimada,
            p.costo_total_partida,
            pu.estatus_pago,
            pu.url_recibo_pago,
            e.fk_id_usuario_capitan,
            (SELECT COUNT(*) FROM "Partida_Usuario" WHERE fk_id_partida = p.id_partida) as total_jugadores
        FROM "Partida_Usuario" pu
        JOIN "Partida" p ON pu.fk_id_partida = p.id_partida
        LEFT JOIN "Equipo" e ON pu.fk_id_equipo_asignado = e.id_equipo
        WHERE pu.fk_id_usuario = :user_id
        """
        result = self.db.execute(text(query), {"user_id": user_id}).fetchall()
        
        payments = []
        for row in result:
            payments.append({
                "id_partida": row.id_partida,
                "nombre_equipo": row.nombre_equipo,
                "url_logo_equipo": row.url_logo_equipo,
                "fecha_inicio_estimada": row.fecha_inicio_estimada,
                "costo_total_partida": float(row.costo_total_partida) if row.costo_total_partida else 0.0,
                "estatus_pago": row.estatus_pago,
                "url_recibo_pago": row.url_recibo_pago,
                "fk_id_usuario_capitan": row.fk_id_usuario_capitan,
                "total_jugadores": row.total_jugadores
            })
        return payments

    def upload_receipt(self, id_partida: int, user_id: int, url_recibo_pago: str, referencia_pago: str) -> None:
        query = """
        UPDATE "Partida_Usuario"
        SET url_recibo_pago = :url, referencia_pago = :referencia, estatus_pago = 'reportado'
        WHERE fk_id_partida = :id_partida AND fk_id_usuario = :user_id
        """
        self.db.execute(text(query), {
            "url": url_recibo_pago,
            "referencia": referencia_pago,
            "id_partida": id_partida,
            "user_id": user_id
        })
        self.db.commit()

    def is_team_captain(self, id_equipo: int, user_id: int) -> bool:
        query = """
        SELECT 1 FROM "Equipo" 
        WHERE id_equipo = :id_equipo AND fk_id_usuario_capitan = :user_id
        """
        result = self.db.execute(text(query), {"id_equipo": id_equipo, "user_id": user_id}).fetchone()
        return bool(result)

    def is_match_captain(self, id_partida: int, user_id: int) -> bool:
        query = """
        SELECT 1 FROM "Equipo" e
        JOIN "Partida_Usuario" pu ON e.id_equipo = pu.fk_id_equipo_asignado
        WHERE pu.fk_id_partida = :id_partida AND e.fk_id_usuario_capitan = :user_id
        """
        result = self.db.execute(text(query), {"id_partida": id_partida, "user_id": user_id}).fetchone()
        return bool(result)

    def get_team_payments(self, id_equipo: int) -> List[Dict]:
        query = """
        SELECT 
            pu.fk_id_partida,
            pu.fk_id_usuario,
            u.nombre_usuario,
            p.fecha_inicio_estimada,
            p.costo_total_partida,
            pu.estatus_pago,
            pu.url_recibo_pago,
            e.fk_id_usuario_capitan,
            (SELECT COUNT(*) FROM "Partida_Usuario" WHERE fk_id_partida = p.id_partida) as total_jugadores
        FROM "Partida_Usuario" pu
        JOIN "Partida" p ON pu.fk_id_partida = p.id_partida
        JOIN "Usuario" u ON pu.fk_id_usuario = u.id_usuario
        JOIN "Equipo" e ON pu.fk_id_equipo_asignado = e.id_equipo
        WHERE pu.fk_id_equipo_asignado = :id_equipo
        """
        result = self.db.execute(text(query), {"id_equipo": id_equipo}).fetchall()
        
        payments = []
        for row in result:
            payments.append({
                "fk_id_partida": row.fk_id_partida,
                "fk_id_usuario": row.fk_id_usuario,
                "nombre_usuario": row.nombre_usuario,
                "fecha_inicio_estimada": row.fecha_inicio_estimada,
                "costo_total_partida": float(row.costo_total_partida) if row.costo_total_partida else 0.0,
                "estatus_pago": row.estatus_pago,
                "url_recibo_pago": row.url_recibo_pago,
                "fk_id_usuario_capitan": row.fk_id_usuario_capitan,
                "total_jugadores": row.total_jugadores
            })
        return payments

    def verify_payment(self, id_partida: int, id_usuario: int) -> None:
        query = """
        UPDATE "Partida_Usuario"
        SET estatus_pago = 'verificado'
        WHERE fk_id_partida = :id_partida AND fk_id_usuario = :id_usuario
        """
        self.db.execute(text(query), {"id_partida": id_partida, "id_usuario": id_usuario})
        self.db.commit()

    def get_payment_captain(self, id_partida: int, user_id: int) -> Optional[int]:
        query = """
        SELECT e.fk_id_usuario_capitan
        FROM "Partida_Usuario" pu
        JOIN "Equipo" e ON pu.fk_id_equipo_asignado = e.id_equipo
        WHERE pu.fk_id_partida = :id_partida AND pu.fk_id_usuario = :user_id
        """
        result = self.db.execute(text(query), {"id_partida": id_partida, "user_id": user_id}).fetchone()
        return result[0] if result else None
