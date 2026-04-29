from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user_id

router = APIRouter(prefix="/payments", tags=["Payments"])

class PaymentResponse(BaseModel):
    id_partida: int
    team_name: str
    team_logo: Optional[str] = None
    concepto: str
    monto: float
    is_paid: bool
    estatus_pago: str
    url_recibo_pago: Optional[str] = None

class UploadReceiptRequest(BaseModel):
    url_recibo_pago: str

@router.get("/my", response_model=List[PaymentResponse])
def get_my_payments(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Obtiene los pagos pendientes y realizados del usuario actual.
    """
    query = """
    SELECT 
        p.id_partida,
        e.nombre_equipo,
        e.url_logo_equipo,
        p.fecha_inicio_estimada,
        p.costo_total_partida,
        pu.estatus_pago,
        pu.url_recibo_pago
    FROM bd_matchday."Partida_Usuario" pu
    JOIN bd_matchday."Partida" p ON pu.fk_id_partida = p.id_partida
    LEFT JOIN bd_matchday."Equipo" e ON pu.fk_id_equipo_asignado = e.id_equipo
    WHERE pu.fk_id_usuario = :user_id
    """
    result = db.execute(text(query), {"user_id": current_user_id}).fetchall()
    
    payments = []
    for row in result:
        # Formatear el concepto con la fecha
        fecha = row.fecha_inicio_estimada.strftime('%d/%m/%Y') if row.fecha_inicio_estimada else ""
        concepto = f"Reserva de Cancha - {fecha}"
        
        payments.append(PaymentResponse(
            id_partida=row.id_partida,
            team_name=row.nombre_equipo if row.nombre_equipo else "Sin Equipo",
            team_logo=row.url_logo_equipo,
            concepto=concepto,
            monto=float(row.costo_total_partida),
            is_paid=(row.estatus_pago == "verificado"),
            estatus_pago=row.estatus_pago,
            url_recibo_pago=row.url_recibo_pago
        ))
    return payments

@router.put("/{id_partida}/upload-receipt")
def upload_receipt(
    id_partida: int,
    request: UploadReceiptRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Sube el comprobante de pago para una partida.
    """
    query = """
    UPDATE bd_matchday."Partida_Usuario"
    SET url_recibo_pago = :url, estatus_pago = 'reportado'
    WHERE fk_id_partida = :id_partida AND fk_id_usuario = :user_id
    """
    result = db.execute(text(query), {
        "url": request.url_recibo_pago,
        "id_partida": id_partida,
        "user_id": current_user_id
    })
    db.commit()
    
    return {"message": "Comprobante reportado exitosamente"}

@router.get("/team/{id_equipo}/validate", response_model=List[dict])
def get_team_payments_to_validate(
    id_equipo: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Obtiene los pagos de los integrantes del equipo para que el capitán valide.
    """
    # Verificar que el usuario sea el capitán del equipo
    verify_query = """
    SELECT 1 FROM bd_matchday."Equipo" 
    WHERE id_equipo = :id_equipo AND fk_id_usuario_capitan = :user_id
    """
    is_captain = db.execute(text(verify_query), {"id_equipo": id_equipo, "user_id": current_user_id}).fetchone()
    if not is_captain:
        raise HTTPException(status_code=403, detail="No eres el capitán de este equipo")

    query = """
    SELECT 
        pu.fk_id_partida,
        pu.fk_id_usuario,
        u.nombre_usuario,
        p.fecha_inicio_estimada,
        p.costo_total_partida,
        pu.estatus_pago,
        pu.url_recibo_pago
    FROM bd_matchday."Partida_Usuario" pu
    JOIN bd_matchday."Partida" p ON pu.fk_id_partida = p.id_partida
    JOIN bd_matchday."Usuario" u ON pu.fk_id_usuario = u.id_usuario
    WHERE pu.fk_id_equipo_asignado = :id_equipo
    """
    result = db.execute(text(query), {"id_equipo": id_equipo}).fetchall()
    
    payments = []
    for row in result:
        fecha = row.fecha_inicio_estimada.strftime('%d/%m/%Y') if row.fecha_inicio_estimada else ""
        payments.append({
            "id_partida": row.fk_id_partida,
            "id_usuario": row.fk_id_usuario,
            "nombre_usuario": row.nombre_usuario,
            "concepto": f"Reserva de Cancha - {fecha}",
            "monto": float(row.costo_total_partida),
            "estatus_pago": row.estatus_pago,
            "url_recibo_pago": row.url_recibo_pago
        })
    return payments

@router.put("/{id_partida}/user/{id_usuario}/verify")
def verify_user_payment(
    id_partida: int,
    id_usuario: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Verifica el pago de un jugador (Solo para el Capitán del equipo).
    """
    # Verificar que el usuario actual sea el capitán
    verify_query = """
    SELECT 1 FROM bd_matchday."Equipo" e
    JOIN bd_matchday."Partida_Usuario" pu ON e.id_equipo = pu.fk_id_equipo_asignado
    WHERE pu.fk_id_partida = :id_partida AND e.fk_id_usuario_capitan = :user_id
    """
    is_captain = db.execute(text(verify_query), {"id_partida": id_partida, "user_id": current_user_id}).fetchone()
    if not is_captain:
        raise HTTPException(status_code=403, detail="No eres el capitán del equipo de esta partida")

    query = """
    UPDATE bd_matchday."Partida_Usuario"
    SET estatus_pago = 'verificado'
    WHERE fk_id_partida = :id_partida AND fk_id_usuario = :id_usuario
    """
    db.execute(text(query), {"id_partida": id_partida, "id_usuario": id_usuario})
    db.commit()
    
    return {"message": "Pago verificado exitosamente"}
