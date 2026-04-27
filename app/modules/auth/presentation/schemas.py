from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class GoogleAuthRequest(BaseModel):
    """
    Esquema para la petición del cliente.
    Recibirá el idToken proveído por Google Sign-In.
    """
    id_token: str = Field(..., description="El idToken obtenido de Google Sign-In en el frontend.")

class RegisterRequest(BaseModel):
    """Esquema para registrar un usuario manualmente."""
    nombre_usuario: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72, description="La contraseña debe tener al menos 6 caracteres y máximo 72.")
    telefono: Optional[str] = None

class LoginRequest(BaseModel):
    """Esquema para iniciar sesión manualmente."""
    email: EmailStr
    password: str = Field(..., max_length=72)

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=72)

class AuthResponse(BaseModel):
    """
    Esquema para la respuesta después de un inicio de sesión exitoso.
    """
    access_token: str
    token_type: str = "bearer"
