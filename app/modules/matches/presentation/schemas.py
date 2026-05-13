from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MatchCreateRequest(BaseModel):
    """Esquema para crear un partido."""
    fecha_inicio_estimada: datetime
    fecha_fin_estimada: datetime
    fk_id_deporte: int
    fk_id_cancha: int
    fk_id_equipo_a: Optional[int] = None

class ProposeTermsRequest(BaseModel):
    """Esquema para proponer términos de negociación."""
    fecha_acordada: datetime
    costo_total: float
    moneda: str = "USD"

class MatchConfigureRequest(BaseModel):
    """Esquema para configurar partido (Capitán)."""
    fecha_acordada: datetime
    costo_total_partida: float
    moneda: str = "USD"
    banco_receptor: str
    cedula_receptor: str
    telefono_receptor: str

class RegisterResultRequest(BaseModel):
    """Esquema para registrar el resultado final."""
    goles_a: int
    goles_b: int

class MatchPlayerResponse(BaseModel):
    """Esquema para un jugador dentro de un partido."""
    id_usuario: int
    nombre_usuario: str
    url_foto_perfil: Optional[str] = None
    estatus_pago: str
    url_recibo_pago: Optional[str] = None
    referencia_pago: Optional[str] = None
    id_equipo: Optional[int] = None

class MatchResponse(BaseModel):
    """Esquema de respuesta de un partido."""
    id: int
    fecha_inicio_estimada: datetime
    fecha_fin_estimada: datetime
    fecha_acordada: Optional[datetime] = None
    costo_total_partida: float
    moneda: str = "USD"
    estatus_partida: str
    fk_id_usuario_org: int
    fk_id_deporte: int
    fk_id_cancha: int
    fk_id_equipo_a: Optional[int] = None
    fk_id_equipo_b: Optional[int] = None
    
    propuesta_fecha_a: Optional[datetime] = None
    propuesta_costo_a: Optional[float] = None
    propuesta_moneda_a: str = "USD"
    propuesta_fecha_b: Optional[datetime] = None
    propuesta_costo_b: Optional[float] = None
    propuesta_moneda_b: str = "USD"
    
    equipo_a_listo: bool = False
    equipo_b_listo: bool = False

    cupos_totales: int
    cuota_por_jugador: float

    # Campos enriquecidos
    nombre_equipo_a: Optional[str] = None
    logo_equipo_a: Optional[str] = None
    nombre_capitan_a: Optional[str] = None
    nombre_cancha: Optional[str] = None
    nombre_deporte: Optional[str] = None
    id_capitan_b: Optional[int] = None
    nombre_equipo_b: Optional[str] = None
    logo_equipo_b: Optional[str] = None
    telefono_capitan_a: Optional[str] = None
    telefono_capitan_b: Optional[str] = None
    resultado_goles_a_cap_a: Optional[int] = None
    resultado_goles_b_cap_a: Optional[int] = None
    resultado_goles_a_cap_b: Optional[int] = None
    resultado_goles_b_cap_b: Optional[int] = None
    latitud_cancha: Optional[float] = None
    longitud_cancha: Optional[float] = None
    backend_status: Optional[str] = None
    banco_receptor: Optional[str] = None
    cedula_receptora: Optional[str] = None
    telefono_receptor: Optional[str] = None
    banco_capitan_b: Optional[str] = None
    cedula_capitan_b: Optional[str] = None
    telefono_capitan_b_pago: Optional[str] = None

    class Config:
        from_attributes = True
