from datetime import datetime, timedelta
from typing import Optional
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests
from passlib.context import CryptContext

from app.core.config import settings

# Contexto para encriptar contraseñas utilizando el algoritmo bcrypt.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su versión hasheada.
    
    :param plain_password: La contraseña enviada por el usuario.
    :param hashed_password: El hash almacenado en la base de datos.
    :return: True si coinciden, False en caso contrario.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Genera un hash seguro a partir de una contraseña en texto plano.
    
    :param password: La contraseña a encriptar.
    :return: El hash resultante (str).
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Genera un JSON Web Token (JWT) firmado para la sesión del usuario.
    
    El token incluye los datos proporcionados y una marca de tiempo de expiración.
    
    :param data: Diccionario con la carga útil (payload) del token.
    :param expires_delta: Periodo de validez personalizado (opcional).
    :return: String del JWT codificado.
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
    Verifica el idToken proporcionado por el flujo de Google Sign-In.
    
    Utiliza la librería oficial de Google Auth para validar la firma y el cliente.
    
    :param token: El token JWT emitido por Google.
    :raises ValueError: Si el token es inválido, ha expirado o el cliente no coincide.
    :return: Diccionario con la información del perfil del usuario en Google.
    """
    try:
        # Verifica el token con Google.
        client_id = settings.GOOGLE_CLIENT_ID if settings.GOOGLE_CLIENT_ID else None
        
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), client_id
        )
        return idinfo
    except ValueError as e:
        raise ValueError(f"Token de Google inválido: {str(e)}")

def create_password_reset_token(email: str) -> str:
    """
    Genera un token JWT temporal y de uso único para el flujo de recuperación de contraseña.
    
    Tiene una validez corta (15 minutos) para minimizar riesgos de seguridad.
    
    :param email: Correo del usuario que solicita el cambio.
    :return: JWT firmado con el tipo 'password_reset'.
    """
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode = {"sub": email, "exp": expire, "type": "password_reset"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Valida un token de restablecimiento de contraseña y extrae el correo asociado.
    
    :param token: El token a verificar.
    :return: El email del usuario si es válido, None en caso de error o expiración.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")
    except jwt.PyJWTError:
        return None

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from app.core.exceptions import UnauthorizedException

# Esquema de seguridad para la extracción automática del token del header Authorization.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """
    Dependencia de FastAPI para autenticar peticiones y obtener el ID del usuario actual.
    
    Decodifica el JWT, valida su integridad y extrae el campo 'sub' (User ID).
    
    :param token: Token extraído del header por oauth2_scheme.
    :raises UnauthorizedException: Si el token es inválido o no contiene el ID del usuario.
    :return: ID del usuario como entero.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException("Token inválido: No se encontró el ID de usuario")
        return int(user_id)
    except (jwt.PyJWTError, ValueError):
        raise UnauthorizedException("Token inválido o expirado")

# Dependencia opcional para rutas que pueden funcionar sin login pero se benefician de él.
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)

def get_optional_user_id(token: Optional[str] = Depends(oauth2_scheme_optional)) -> Optional[int]:
    """Retorna el ID del usuario si el token es válido, de lo contrario None."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        return int(user_id) if user_id else None
    except:
        return None

def create_team_invitation_token(team_id: int) -> str:
    """
    Genera un token firmado para invitar a usuarios a un equipo de forma directa.
    
    :param team_id: ID del equipo al que se invita.
    :return: JWT con validez de 30 minutos y tipo 'team_invitation'.
    """
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode = {"team_id": team_id, "exp": expire, "type": "team_invitation"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_team_invitation_token(token: str) -> Optional[int]:
    """
    Verifica un token de invitación a equipo y retorna el ID del equipo.
    
    :param token: Token de invitación.
    :return: ID del equipo si es válido, None en caso contrario.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "team_invitation":
            return None
        return payload.get("team_id")
    except jwt.PyJWTError:
        return None
