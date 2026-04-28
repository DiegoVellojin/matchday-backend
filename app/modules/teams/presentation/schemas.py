from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.modules.catalogs.presentation.schemas import DeporteResponse

class TeamCreateRequest(BaseModel):
    """Esquema para crear un equipo."""
    nombre_equipo: str = Field(..., min_length=3, max_length=100)
    fk_id_deporte: int
    url_logo_equipo: Optional[str] = None
    descripcion_equipo: Optional[str] = None
    esta_reclutando: bool = True
    max_miembros: int = 11

class TeamResponse(BaseModel):
    """Esquema para devolver la información de un equipo."""
    id_equipo: int
    nombre_equipo: str
    fk_id_deporte: int
    deporte: Optional[DeporteResponse] = None
    fk_id_usuario_capitan: Optional[int]
    url_logo_equipo: Optional[str] = None
    puntos_acumulados: int
    descripcion_equipo: Optional[str]
    esta_reclutando: bool
    max_miembros: int
    miembros_actuales: int = 1
    fecha_creacion_equipo: datetime


    class Config:
        from_attributes = True

class MemberResponse(BaseModel):
    """Esquema para devolver la información de un miembro de equipo."""
    fk_id_equipo: int
    fk_id_usuario: int
    estatus_miembro: str
    rol_equipo: str

    class Config:
        from_attributes = True

class RespondRequest(BaseModel):
    """Esquema para aceptar/rechazar solicitud."""
    accept: bool
