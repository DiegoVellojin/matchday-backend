from typing import Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from app.core.events import AggregateRoot
from app.modules.matches.domain.events import TeamAssignedToMatch

@dataclass
class MatchEntity(AggregateRoot):
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
    cupos_totales: int = 22
    jugadores_inscritos: int = 0

    # Campos para la negociación entre capitanes
    propuesta_fecha_a: Optional[datetime] = None
    propuesta_costo_a: Optional[float] = None
    propuesta_fecha_b: Optional[datetime] = None
    propuesta_costo_b: Optional[float] = None
    equipo_a_listo: bool = False
    equipo_b_listo: bool = False

    # Verificación Cruzada de Resultados
    resultado_goles_a_cap_a: Optional[int] = None
    resultado_goles_b_cap_a: Optional[int] = None
    resultado_goles_a_cap_b: Optional[int] = None
    resultado_goles_b_cap_b: Optional[int] = None

    # Campos enriquecidos para visualización (Movidos arriba para verificar serialización)
    id_capitan_b: Optional[int] = None
    nombre_equipo_b: Optional[str] = None
    logo_equipo_b: Optional[str] = None
    nombre_equipo_a: Optional[str] = None
    logo_equipo_a: Optional[str] = None
    nombre_capitan_a: Optional[str] = None
    nombre_cancha: Optional[str] = None
    nombre_deporte: Optional[str] = None
    telefono_capitan_a: Optional[str] = None
    telefono_capitan_b: Optional[str] = None
    latitud_cancha: Optional[float] = None
    longitud_cancha: Optional[float] = None
    banco_receptor: Optional[str] = None
    cedula_receptora: Optional[str] = None
    telefono_receptor: Optional[str] = None
    banco_capitan_b: Optional[str] = None
    cedula_capitan_b: Optional[str] = None
    telefono_capitan_b_pago: Optional[str] = None
    backend_status: str = "UPDATED_V3"

    def __post_init__(self):
        super().__init__()

    @property
    def cuota_por_jugador(self) -> float:
        """Propiedad calculada que retorna de forma segura costo_total / max(1, jugadores_inscritos)."""
        divisor = max(1, getattr(self, 'jugadores_inscritos', 0))
        return round(self.costo_total_partida / divisor, 2)

    def assign_team_a(self, team_id: int):
        """Asigna el equipo A y registra el evento."""
        if self.fk_id_equipo_a != team_id:
            self.fk_id_equipo_a = team_id
            if self.id:
                self.record_event(TeamAssignedToMatch(match_id=self.id, team_id=team_id))

    def assign_team_b(self, team_id: int):
        """Asigna el equipo B y registra el evento."""
        if self.fk_id_equipo_b != team_id:
            self.fk_id_equipo_b = team_id
            if self.id:
                self.record_event(TeamAssignedToMatch(match_id=self.id, team_id=team_id))

    def can_transition_to_pending_payment(self) -> bool:
        """Verifica si ambas propuestas coinciden para avanzar a pendiente_pago."""
        if not self.propuesta_fecha_a or not self.propuesta_fecha_b:
            return False
        if self.propuesta_costo_a is None or self.propuesta_costo_b is None:
            return False
        return (self.propuesta_fecha_a == self.propuesta_fecha_b and 
                self.propuesta_costo_a == self.propuesta_costo_b)
