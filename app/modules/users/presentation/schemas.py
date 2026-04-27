from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserResponse(BaseModel):
    """Esquema para devolver la información del usuario."""
    id_usuario: int
    nombre_usuario: str
    email_usuario: EmailStr
    telefono_usuario: Optional[str] = None
    url_foto_perfil: Optional[str] = None
    rol_usuario: str
    reliability_score: float

    class Config:
        from_attributes = True

class UpdateUserRequest(BaseModel):
    """Esquema para recibir los datos a actualizar."""
    nombre_usuario: Optional[str] = Field(None, min_length=2, max_length=100)
    telefono_usuario: Optional[str] = Field(None, max_length=20)
    url_foto_perfil: Optional[str] = Field(None, max_length=255)
