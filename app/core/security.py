from datetime import datetime, timedelta
from typing import Optional
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests

from app.core.config import settings

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Genera un JSON Web Token (JWT) firmado para la sesión del usuario.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_google_token(token: str) -> dict:
    """
    Verifica el idToken proporcionado por Google Sign-In.
    Retorna la información del usuario si es válido, lanza ValueError si no.
    """
    try:
        # Verifica el token con Google. Si el CLIENT_ID está configurado,
        # lo valida. Si no, solo valida la firma de Google.
        client_id = settings.GOOGLE_CLIENT_ID if settings.GOOGLE_CLIENT_ID else None
        
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), client_id
        )
        return idinfo
    except ValueError as e:
        # Token inválido
        raise ValueError(f"Token de Google inválido: {str(e)}")
