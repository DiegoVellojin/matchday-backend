from typing import Optional, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class MatchEntity:
    """Entidad que representa un partido o encuentro deportivo."""
    id: Optional[int] = None
    fecha_inicio_estimada: datetime = field(default_factory=datetime.now)
    fecha_fin_estimada: datetime = field(default_factory=datetime.now)
    fecha_acordada: Optional[datetime] = None
    costo_total_partida: float = 0.0
    estatus_partida: str = "publicada"
    fk_id_usuario_org: int = 0
    fk_id_deporte: int = 0
    fk_id_cancha: int = 0
    fk_id_equipo_a: Optional[int] = None
    fk_id_equipo_b: Optional[int] = None
    fecha_creacion_partida: datetime = field(default_factory=datetime.now)

    # Campos para la negociación entre capitanes
    propuesta_fecha_a: Optional[datetime] = None
    propuesta_costo_a: Optional[float] = None
    propuesta_fecha_b: Optional[datetime] = None
    propuesta_costo_b: Optional[float] = None

    # Campos enriquecidos para visualización
    nombre_equipo_a: Optional[str] = None
    logo_equipo_a: Optional[str] = None
    nombre_capitan_a: Optional[str] = None
    nombre_cancha: Optional[str] = None
    nombre_deporte: Optional[str] = None

    def can_transition_to_pending_payment(self) -> bool:
        """Verifica si ambas propuestas coinciden para avanzar a pendiente_pago."""
        if not self.propuesta_fecha_a or not self.propuesta_fecha_b:
            return False
        return (self.propuesta_fecha_a == self.propuesta_fecha_b and 
                self.propuesta_costo_a == self.propuesta_costo_b)
