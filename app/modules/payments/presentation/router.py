from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.modules.payments.infrastructure.repositories_impl import PaymentRepositoryImpl
from app.modules.payments.application.use_cases import (
    GetMyPaymentsUseCase, 
    UploadReceiptUseCase, 
    GetTeamPaymentsToValidateUseCase, 
    VerifyUserPaymentUseCase
)
from app.modules.notifications.infrastructure.repositories_impl import NotificacionRepositoryImpl
from app.modules.notifications.application.use_cases import CreateNotificationUseCase

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
    referencia_pago: str

@router.get("/my", response_model=List[PaymentResponse])
def get_my_payments(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Obtiene los pagos pendientes y realizados del usuario actual."""
    repository = PaymentRepositoryImpl(db)
    use_case = GetMyPaymentsUseCase(repository)
    
    raw_payments = use_case.execute(current_user_id)
    payments = []
    
    for row in raw_payments:
        fecha = row["fecha_inicio_estimada"].strftime('%d/%m/%Y') if row["fecha_inicio_estimada"] else ""
        concepto = f"Reserva de Cancha - {fecha}"
        
        payments.append(PaymentResponse(
            id_partida=row["id_partida"],
            team_name=row["nombre_equipo"] if row["nombre_equipo"] else "Sin Equipo",
            team_logo=row["url_logo_equipo"],
            concepto=concepto,
            monto=row["costo_total_partida"],
            is_paid=(row["estatus_pago"] == "verificado"),
            estatus_pago=row["estatus_pago"],
            url_recibo_pago=row["url_recibo_pago"]
        ))
    return payments

@router.post("/{id_partida}/upload")
def upload_receipt(
    id_partida: int,
    request: UploadReceiptRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Sube el comprobante de pago para una partida."""
    repository = PaymentRepositoryImpl(db)
    use_case = UploadReceiptUseCase(repository)
    
    use_case.execute(id_partida, current_user_id, request.url_recibo_pago, request.referencia_pago)
    
    # Notificar al organizador / capitán
    try:
        from app.modules.matches.infrastructure.repositories_impl import MatchRepositoryImpl
        match_repo = MatchRepositoryImpl(db)
        match = match_repo.get_by_id(id_partida)
        if match:
            # Enviar notificación FCM al organizador o capitán
            notif_repo = NotificacionRepositoryImpl(db)
            notif_use_case = CreateNotificationUseCase(notif_repo)
            
            # Buscamos el nombre del jugador para la notificación
            from app.modules.users.infrastructure.repositories_impl import UserRepositoryImpl
            user_repo = UserRepositoryImpl(db)
            user = user_repo.get_user_by_id(current_user_id)
            user_name = user.name if user else "Un jugador"
            
            # Determinamos a quién notificar (al capitán del equipo del usuario, o al organizador)
            # Para simplificar, notificaremos al organizador (quien usualmente gestiona los pagos)
            # o al capitán que corresponda. Aquí usamos fk_id_usuario_org.
            notif_use_case.execute(
                id_usuario=match.fk_id_usuario_org,
                mensaje=f"{user_name} ha subido su comprobante de pago. Por favor verifícalo.",
                tipo="receipt_uploaded",
                referencia_id=id_partida,
                db=db
            )
    except Exception as e:
        print(f"Error al enviar notificación FCM en upload_receipt: {e}")
        
    return {"message": "Comprobante reportado exitosamente"}

@router.get("/team/{id_equipo}/validate", response_model=List[dict])
def get_team_payments_to_validate(
    id_equipo: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Obtiene los pagos de los integrantes del equipo para que el capitán valide."""
    repository = PaymentRepositoryImpl(db)
    use_case = GetTeamPaymentsToValidateUseCase(repository)
    
    raw_payments = use_case.execute(id_equipo, current_user_id)
    
    payments = []
    for row in raw_payments:
        fecha = row["fecha_inicio_estimada"].strftime('%d/%m/%Y') if row["fecha_inicio_estimada"] else ""
        payments.append({
            "id_partida": row["fk_id_partida"],
            "id_usuario": row["fk_id_usuario"],
            "nombre_usuario": row["nombre_usuario"],
            "concepto": f"Reserva de Cancha - {fecha}",
            "monto": row["costo_total_partida"],
            "estatus_pago": row["estatus_pago"],
            "url_recibo_pago": row["url_recibo_pago"]
        })
    return payments

@router.put("/verify")
def verify_user_payment(
    id_partida: int,
    id_usuario: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Verifica el pago de un jugador (Solo para el Capitán del equipo)."""
    repository = PaymentRepositoryImpl(db)
    use_case = VerifyUserPaymentUseCase(repository)
    
    use_case.execute(id_partida, id_usuario, current_user_id)
    
    # Enviar notificación FCM al jugador
    try:
        notif_repo = NotificacionRepositoryImpl(db)
        notif_use_case = CreateNotificationUseCase(notif_repo)
        notif_use_case.execute(
            id_usuario=id_usuario,
            mensaje=f"Tu pago ha sido verificado exitosamente por el capitán.",
            tipo="payment_verified",
            referencia_id=id_partida,
            db=db
        )
    except Exception as e:
        print(f"Error al enviar notificación FCM en verify_user_payment: {e}")
        
    return {"message": "Pago verificado exitosamente"}
