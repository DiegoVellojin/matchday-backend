from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.modules.users.infrastructure.repositories_impl import UsuarioRepositoryImpl
from app.modules.users.application.use_cases import GetUserProfileUseCase, UpdateUserProfileUseCase
from app.modules.users.presentation.schemas import UserResponse, UpdateUserRequest

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna el perfil del usuario autenticado.
    """
    repo = UsuarioRepositoryImpl(db)
    use_case = GetUserProfileUseCase(repo)
    
    usuario = use_case.execute(current_user_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return usuario

@router.put("/me", response_model=UserResponse)
def update_my_profile(
    request: UpdateUserRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos del perfil del usuario (nombre, teléfono, foto).
    """
    repo = UsuarioRepositoryImpl(db)
    use_case = UpdateUserProfileUseCase(repo)
    
    try:
        usuario = use_case.execute(
            id_usuario=current_user_id,
            nombre=request.nombre_usuario,
            telefono=request.telefono_usuario,
            foto_url=request.url_foto_perfil
        )
        return usuario
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

from app.modules.users.infrastructure.repositories_impl import FCMRepositoryImpl
from app.modules.users.presentation.schemas import FCMTokenRequest

@router.post("/fcm-token")
def register_fcm_token(
    request: FCMTokenRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Registra el token FCM del dispositivo móvil del usuario autenticado.
    """
    repo = FCMRepositoryImpl(db)
    repo.save_token(id_usuario=current_user_id, fcm_token=request.fcm_token)
    return {"message": "Token FCM registrado con éxito"}

