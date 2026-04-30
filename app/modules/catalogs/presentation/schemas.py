from pydantic import BaseModel
from typing import Optional

class DeporteResponse(BaseModel):
    id_deporte: int
    nombre_deporte: str

    class Config:
        from_attributes = True

class RegionResponse(BaseModel):
    id_region: int
    nombre_region: str
    fk_id_region: Optional[int] = None

    class Config:
        from_attributes = True

class CanchaResponse(BaseModel):
    id_cancha: int
    nombre_cancha: str
    direccion_cancha: Optional[str] = None
    fk_id_region: int

    class Config:
        from_attributes = True
