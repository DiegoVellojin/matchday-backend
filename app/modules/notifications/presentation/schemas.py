from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificationResponse(BaseModel):
    id_notificacion: int
    fk_id_usuario: int
    mensaje: str
    leida: bool
    fecha_creacion: datetime
    tipo: Optional[str] = None
    referencia_id: Optional[int] = None

    class Config:
        from_attributes = True
