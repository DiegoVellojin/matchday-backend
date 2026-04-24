from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.modules.auth.presentation.schemas import GoogleAuthRequest, AuthResponse
from app.modules.auth.application.use_cases import GoogleLoginUseCase
from app.modules.auth.infrastructure.repositories_impl import UsuarioRepositoryImpl
from app.modules.auth.domain.exceptions import InvalidGoogleTokenException

router = APIRouter()

@router.post("/google", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def google_login(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Endpoint para autenticar a un usuario con Google Sign-In.
    """
    # 1. Instanciamos el repositorio con la BD inyectada
    usuario_repo = UsuarioRepositoryImpl(db)
    
    # 2. Instanciamos el caso de uso
    use_case = GoogleLoginUseCase(usuario_repository=usuario_repo)
    
    # 3. Ejecutamos el caso de uso
    try:
        token = use_case.execute(id_token=request.id_token)
        return AuthResponse(access_token=token)
    except InvalidGoogleTokenException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        # En caso de error de base de datos u otro error genérico
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el servidor al autenticar: {str(e)}"
        )
