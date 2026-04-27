from datetime import datetime, timedelta
from typing import Optional
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests
from passlib.context import CryptContext

from app.core.config import settings

# Contexto para encriptar contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera un hash bcrypt a partir de una contraseña"""
    return pwd_context.hash(password)

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

def create_password_reset_token(email: str) -> str:
    """
    Genera un token JWT temporal para el restablecimiento de contraseña (15 minutos).
    """
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode = {"sub": email, "exp": expire, "type": "password_reset"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verifica un token de restablecimiento de contraseña.
    Retorna el email asociado si es válido, None si es inválido o expiró.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")
    except jwt.PyJWTError:
        return None

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """
    Dependencia para obtener el ID del usuario desde el JWT.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: No se encontró el ID de usuario",
            )
        return int(user_id)
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )

def create_team_invitation_token(team_id: int) -> str:
    """
    Genera un token firmado para invitar a un equipo (30 minutos de duración).
    """
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode = {"team_id": team_id, "exp": expire, "type": "team_invitation"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_team_invitation_token(token: str) -> Optional[int]:
    """
    Verifica un token de invitación. Retorna el ID del equipo si es válido.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "team_invitation":
            return None
        return payload.get("team_id")
    except jwt.PyJWTError:
        return None
