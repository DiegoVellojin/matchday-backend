from pydantic import BaseModel

class DeporteResponse(BaseModel):
    id_deporte: int
    nombre_deporte: str

    class Config:
        from_attributes = True
