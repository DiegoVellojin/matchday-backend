from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.modules.teams.infrastructure.repositories_impl import EquipoRepositoryImpl
from app.modules.teams.application.use_cases import CreateTeamUseCase, RequestJoinTeamUseCase, GetMyTeamsUseCase, JoinTeamWithTokenUseCase, GetPendingMembersUseCase, RespondToJoinRequestUseCase, GetDiscoverableTeamsUseCase

from app.modules.teams.presentation.schemas import TeamCreateRequest, TeamResponse, MemberResponse, RespondRequest

router = APIRouter()

@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    request: TeamCreateRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo equipo y asigna al usuario actual como Capitán.
    """
    repo = EquipoRepositoryImpl(db)
    use_case = CreateTeamUseCase(repo)
    
    return use_case.execute(
        nombre=request.nombre_equipo,
        id_deporte=request.fk_id_deporte,
        id_usuario_creador=current_user_id,
        url_logo=request.url_logo_equipo,
        descripcion=request.descripcion_equipo,
        esta_reclutando=request.esta_reclutando,
        max_miembros=request.max_miembros
    )

@router.get("/", response_model=List[TeamResponse])
def get_discoverable_teams(
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de todos los equipos que están reclutando miembros.
    """
    repo = EquipoRepositoryImpl(db)
    use_case = GetDiscoverableTeamsUseCase(repo)
    
    return use_case.execute()


@router.get("/me", response_model=List[TeamResponse])
def get_my_teams(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de equipos a los que pertenece el usuario actual.
    """
    repo = EquipoRepositoryImpl(db)
    use_case = GetMyTeamsUseCase(repo)
    
    return use_case.execute(id_usuario=current_user_id)

@router.post("/{id_equipo}/join", response_model=MemberResponse)
def join_team(
    id_equipo: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Solicita unirse a un equipo existente (requiere aprobación posterior).
    """
    repo = EquipoRepositoryImpl(db)
    use_case = RequestJoinTeamUseCase(repo)
    
    if not repo.get_by_id(id_equipo):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado")
        
    return use_case.execute(id_equipo=id_equipo, id_usuario=current_user_id)

@router.get("/{id_equipo}/invite-token")
def get_invite_token(
    id_equipo: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Genera un token de invitación de 30 min. Solo para el Capitán.
    """
    repo = EquipoRepositoryImpl(db)
    equipo = repo.get_by_id(id_equipo)
    
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    
    if equipo.fk_id_usuario_capitan != current_user_id:
        raise HTTPException(status_code=403, detail="Solo el capitán puede generar invitaciones.")
    
    from app.core.security import create_team_invitation_token
    token = create_team_invitation_token(id_equipo)
    return {"invitation_token": token}

@router.post("/join-with-token", response_model=MemberResponse)
def join_with_token(
    token: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Se une a un equipo inmediatamente usando un token válido.
    """
    repo = EquipoRepositoryImpl(db)
    use_case = JoinTeamWithTokenUseCase(repo)
    
    try:
        return use_case.execute(token=token, id_usuario=current_user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id_equipo}/requests", response_model=List[MemberResponse])
def get_pending_requests(
    id_equipo: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista las solicitudes pendientes. Solo para el Capitán.
    """
    repo = EquipoRepositoryImpl(db)
    equipo = repo.get_by_id(id_equipo)
    
    if not equipo or equipo.fk_id_usuario_capitan != current_user_id:
        raise HTTPException(status_code=403, detail="Acceso denegado.")
    
    use_case = GetPendingMembersUseCase(repo)
    return use_case.execute(id_equipo)

@router.put("/{id_equipo}/requests/{id_usuario}")
def respond_to_request(
    id_equipo: int,
    id_usuario: int,
    request: RespondRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Acepta o rechaza una solicitud. Solo para el Capitán.
    Si se rechaza, el registro se elimina de la BD.
    """
    repo = EquipoRepositoryImpl(db)
    equipo = repo.get_by_id(id_equipo)
    
    if not equipo or equipo.fk_id_usuario_capitan != current_user_id:
        raise HTTPException(status_code=403, detail="Acceso denegado.")
    
    use_case = RespondToJoinRequestUseCase(repo)
    success = use_case.execute(id_equipo, id_usuario, request.accept)
    
    if not success:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
    
    return {"message": "Solicitud procesada correctamente."}
