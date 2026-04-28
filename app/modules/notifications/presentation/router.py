from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db, engine
from app.core.security import get_current_user_id

from app.modules.notifications.presentation.schemas import NotificationResponse
from app.modules.notifications.application.use_cases import GetMyNotificationsUseCase, MarkNotificationAsReadUseCase
from app.modules.notifications.infrastructure.repositories_impl import NotificacionRepositoryImpl

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# Nos aseguramos de que la tabla exista en Neon DB
def _create_table_if_not_exists():
    query = """
    CREATE TABLE IF NOT EXISTS bd_matchday."Notificacion" (
        id_notificacion SERIAL PRIMARY KEY,
        fk_id_usuario INT NOT NULL,
        mensaje VARCHAR(255) NOT NULL,
        leida BOOLEAN DEFAULT FALSE,
        fecha_creacion TIMESTAMP DEFAULT NOW(),
        tipo VARCHAR(50),
        referencia_id INT
    );
    """
    with engine.connect() as connection:
        connection.execute(text(query))
        connection.commit()

try:
    _create_table_if_not_exists()
except Exception as e:
    print(f"Advertencia al verificar/crear tabla Notificacion: {e}")

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las notificaciones del usuario autenticado.
    """
    repo = NotificacionRepositoryImpl(db)
    use_case = GetMyNotificationsUseCase(repo)
    return use_case.execute(current_user_id)

@router.put("/{id_notificacion}/read")
def mark_as_read(
    id_notificacion: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Marca una notificación como leída.
    """
    repo = NotificacionRepositoryImpl(db)
    use_case = MarkNotificationAsReadUseCase(repo)
    success = use_case.execute(id_notificacion, current_user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada o no pertenece al usuario."
        )
    return {"message": "Notificación marcada como leída."}
