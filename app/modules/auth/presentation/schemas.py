from pydantic import BaseModel, Field

class GoogleAuthRequest(BaseModel):
    """
    Esquema para la petición del cliente.
    Recibirá el idToken proveído por Google Sign-In.
    """
    id_token: str = Field(..., description="El idToken obtenido de Google Sign-In en el frontend.")

class AuthResponse(BaseModel):
    """
    Esquema para la respuesta después de un inicio de sesión exitoso.
    """
    access_token: str
    token_type: str = "bearer"
