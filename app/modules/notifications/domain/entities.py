from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Notificacion:
    id_notificacion: Optional[int]
    fk_id_usuario: int
    mensaje: str
    leida: bool
    fecha_creacion: datetime
    # Opcional: para redirigir en el front al pulsarla
    tipo: Optional[str] = None # 'join_request', 'accepted', 'rejected'
    referencia_id: Optional[int] = None # ID del equipo o partido relevante
