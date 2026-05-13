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
            p.moneda,
            pu.estatus_pago,
            pu.url_recibo_pago,
            e.fk_id_usuario_capitan,
            db.banco as banco_receptor,
            db.cedula as cedula_receptora,
            db.telefono as telefono_receptor,
            (SELECT COUNT(*) FROM bd_matchday."Partida_Usuario" WHERE fk_id_partida = p.id_partida) as total_jugadores
        FROM bd_matchday."Partida_Usuario" pu
        JOIN bd_matchday."Partida" p ON pu.fk_id_partida = p.id_partida
        LEFT JOIN bd_matchday."Equipo" e ON pu.fk_id_equipo_asignado = e.id_equipo
        LEFT JOIN bd_matchday."Datos_Bancarios" db ON e.fk_id_usuario_capitan = db.fk_id_usuario
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
                "moneda": row.moneda,
                "estatus_pago": row.estatus_pago,
                "url_recibo_pago": row.url_recibo_pago,
                "fk_id_usuario_capitan": row.fk_id_usuario_capitan,
                "total_jugadores": row.total_jugadores,
                "banco_receptor": row.banco_receptor,
                "cedula_receptora": row.cedula_receptora,
                "telefono_receptor": row.telefono_receptor
            })
        return payments

    def upload_receipt(self, id_partida: int, user_id: int, url_recibo_pago: str, referencia_pago: str, tasa_usada_bs: Optional[float] = None) -> None:
        monto_pagado_bs = None
        
        if tasa_usada_bs:
            # Calculamos el monto en BS congelando la tasa en este momento
            calc_query = """
            SELECT p.costo_total_partida, 
                   (SELECT COUNT(*) FROM bd_matchday."Partida_Usuario" WHERE fk_id_partida = p.id_partida) as total_jugadores
            FROM bd_matchday."Partida" p
            WHERE p.id_partida = :id_partida
            """
            match_data = self.db.execute(text(calc_query), {"id_partida": id_partida}).fetchone()
            if match_data:
                costo_total = float(match_data.costo_total_partida)
                total_jugadores = match_data.total_jugadores
                monto_divisa = costo_total / total_jugadores if total_jugadores > 0 else costo_total
                monto_pagado_bs = monto_divisa * tasa_usada_bs

        query = """
        UPDATE bd_matchday."Partida_Usuario"
        SET url_recibo_pago = :url, 
            referencia_pago = :referencia, 
            estatus_pago = 'reportado',
            tasa_usada_bs = :tasa,
            monto_pagado_bs = :monto_bs
        WHERE fk_id_partida = :id_partida AND fk_id_usuario = :user_id
        """
        self.db.execute(text(query), {
            "url": url_recibo_pago,
            "referencia": referencia_pago,
            "id_partida": id_partida,
            "user_id": user_id,
            "tasa": tasa_usada_bs,
            "monto_bs": monto_pagado_bs
        })
        self.db.commit()

    def is_team_captain(self, id_equipo: int, user_id: int) -> bool:
        query = """
        SELECT 1 FROM bd_matchday."Equipo" 
        WHERE id_equipo = :id_equipo AND fk_id_usuario_capitan = :user_id
        """
        result = self.db.execute(text(query), {"id_equipo": id_equipo, "user_id": user_id}).fetchone()
        return bool(result)

    def is_match_captain(self, id_partida: int, user_id: int) -> bool:
        query = """
        SELECT 1 FROM bd_matchday."Equipo" e
        JOIN bd_matchday."Partida_Usuario" pu ON e.id_equipo = pu.fk_id_equipo_asignado
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
            (SELECT COUNT(*) FROM bd_matchday."Partida_Usuario" WHERE fk_id_partida = p.id_partida) as total_jugadores
        FROM bd_matchday."Partida_Usuario" pu
        JOIN bd_matchday."Partida" p ON pu.fk_id_partida = p.id_partida
        JOIN bd_matchday."Usuario" u ON pu.fk_id_usuario = u.id_usuario
        JOIN bd_matchday."Equipo" e ON pu.fk_id_equipo_asignado = e.id_equipo
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
        UPDATE bd_matchday."Partida_Usuario"
        SET estatus_pago = 'verificado'
        WHERE fk_id_partida = :id_partida AND fk_id_usuario = :id_usuario
        """
        self.db.execute(text(query), {"id_partida": id_partida, "id_usuario": id_usuario})
        self.db.commit()

    def get_payment_captain(self, id_partida: int, user_id: int) -> Optional[int]:
        query = """
        SELECT e.fk_id_usuario_capitan
        FROM bd_matchday."Partida_Usuario" pu
        JOIN bd_matchday."Equipo" e ON pu.fk_id_equipo_asignado = e.id_equipo
        WHERE pu.fk_id_partida = :id_partida AND pu.fk_id_usuario = :user_id
        """
        result = self.db.execute(text(query), {"id_partida": id_partida, "user_id": user_id}).fetchone()
        return result[0] if result else None
