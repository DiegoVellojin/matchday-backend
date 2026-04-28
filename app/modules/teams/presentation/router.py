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
    
    equipo = use_case.execute(
        nombre=request.nombre_equipo,
        id_deporte=request.fk_id_deporte,
        id_usuario_creador=current_user_id,
        url_logo=request.url_logo_equipo,
        descripcion=request.descripcion_equipo,
        esta_reclutando=request.esta_reclutando,
        max_miembros=request.max_miembros
    )
    
    eq_dict = equipo.__dict__.copy()
    eq_dict["miembros_actuales"] = 1
    return eq_dict


@router.get("/", response_model=List[TeamResponse])
def get_discoverable_teams(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de todos los equipos que están reclutando miembros.
    """
    repo = EquipoRepositoryImpl(db)
    use_case = GetDiscoverableTeamsUseCase(repo)
    equipos = use_case.execute()
    
    from app.modules.teams.infrastructure.orm_models import EquipoUsuarioORM
    
    response = []
    for eq in equipos:
        count = db.query(EquipoUsuarioORM).filter(
            EquipoUsuarioORM.fk_id_equipo == eq.id_equipo,
            EquipoUsuarioORM.estatus_miembro == 'aceptado'
        ).count()
        
        es_miembro = db.query(EquipoUsuarioORM).filter(
            EquipoUsuarioORM.fk_id_equipo == eq.id_equipo,
            EquipoUsuarioORM.fk_id_usuario == current_user_id,
            EquipoUsuarioORM.estatus_miembro == 'aceptado'
        ).first() is not None
        
        eq_dict = eq.__dict__.copy()
        eq_dict["miembros_actuales"] = count if count > 0 else 1
        eq_dict["soy_miembro"] = es_miembro
        response.append(eq_dict)
    return response


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
    equipos = use_case.execute(id_usuario=current_user_id)
    
    from app.modules.teams.infrastructure.orm_models import EquipoUsuarioORM
    
    response = []
    for eq in equipos:
        count = db.query(EquipoUsuarioORM).filter(
            EquipoUsuarioORM.fk_id_equipo == eq.id_equipo,
            EquipoUsuarioORM.estatus_miembro == 'aceptado'
        ).count()
        eq_dict = eq.__dict__.copy()
        eq_dict["miembros_actuales"] = count if count > 0 else 1
        eq_dict["soy_miembro"] = True
        response.append(eq_dict)
    return response



@router.get("/{id_equipo}", response_model=TeamResponse)
def get_team_detail(
    id_equipo: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles de un equipo por su ID.
    """
    repo = EquipoRepositoryImpl(db)
    equipo = repo.get_by_id(id_equipo)
    
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado.")
        
    from app.modules.teams.infrastructure.orm_models import EquipoUsuarioORM
    
    count = db.query(EquipoUsuarioORM).filter(
        EquipoUsuarioORM.fk_id_equipo == equipo.id_equipo,
        EquipoUsuarioORM.estatus_miembro == 'aceptado'
    ).count()
    
    es_miembro = db.query(EquipoUsuarioORM).filter(
        EquipoUsuarioORM.fk_id_equipo == equipo.id_equipo,
        EquipoUsuarioORM.fk_id_usuario == current_user_id,
        EquipoUsuarioORM.estatus_miembro == 'aceptado'
    ).first() is not None
    
    eq_dict = equipo.__dict__.copy()
    eq_dict["miembros_actuales"] = count if count > 0 else 1
    eq_dict["soy_miembro"] = es_miembro
    return eq_dict


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
        
    try:
        resultado = use_case.execute(id_equipo=id_equipo, id_usuario=current_user_id)
        
        # Crear notificación para el capitán
        equipo = repo.get_by_id(id_equipo)
        if equipo and equipo.fk_id_usuario_capitan:
            from app.modules.notifications.infrastructure.repositories_impl import NotificacionRepositoryImpl
            from app.modules.notifications.application.use_cases import CreateNotificationUseCase
            
            notif_repo = NotificacionRepositoryImpl(db)
            notif_use_case = CreateNotificationUseCase(notif_repo)
            mensaje = f"Un nuevo jugador ha solicitado unirse a tu equipo '{equipo.nombre_equipo}'."
            notif_use_case.execute(
                id_usuario=equipo.fk_id_usuario_capitan,
                mensaje=mensaje,
                tipo="join_request",
                referencia_id=id_equipo,
                db=db
            )

            
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))



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
        
    from app.modules.teams.infrastructure.orm_models import EquipoUsuarioORM
    from app.modules.users.infrastructure.orm_models import UsuarioORM
    
    results = db.query(EquipoUsuarioORM, UsuarioORM).join(
        UsuarioORM, EquipoUsuarioORM.fk_id_usuario == UsuarioORM.id_usuario
    ).filter(
        EquipoUsuarioORM.fk_id_equipo == id_equipo,
        EquipoUsuarioORM.estatus_miembro == "pendiente"
    ).all()
    
    response = []
    for member, user in results:
        m_dict = member.__dict__.copy()
        m_dict["nombre_usuario"] = user.nombre_usuario
        m_dict["email_usuario"] = user.email_usuario
        m_dict["url_foto_perfil"] = user.url_foto_perfil
        response.append(m_dict)
        
    return response


@router.get("/{id_equipo}/members", response_model=List[MemberResponse])
def get_team_members(
    id_equipo: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista todos los miembros aceptados de un equipo.
    """
    from app.modules.teams.infrastructure.orm_models import EquipoUsuarioORM
    from app.modules.users.infrastructure.orm_models import UsuarioORM
    
    results = db.query(EquipoUsuarioORM, UsuarioORM).join(

        UsuarioORM, EquipoUsuarioORM.fk_id_usuario == UsuarioORM.id_usuario
    ).filter(
        EquipoUsuarioORM.fk_id_equipo == id_equipo,
        EquipoUsuarioORM.estatus_miembro == "aceptado"
    ).all()
    
    response = []
    for member, user in results:
        m_dict = member.__dict__.copy()
        m_dict["nombre_usuario"] = user.nombre_usuario
        m_dict["email_usuario"] = user.email_usuario
        m_dict["url_foto_perfil"] = user.url_foto_perfil
        response.append(m_dict)
        
    return response


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
        
    # Crear notificación para el jugador
    from app.modules.notifications.infrastructure.repositories_impl import NotificacionRepositoryImpl
    from app.modules.notifications.application.use_cases import CreateNotificationUseCase
    
    notif_repo = NotificacionRepositoryImpl(db)
    notif_use_case = CreateNotificationUseCase(notif_repo)
    
    accion = "aceptada" if request.accept else "rechazada"
    mensaje = f"Tu solicitud para unirte al equipo '{equipo.nombre_equipo}' ha sido {accion}."
    tipo = "accepted" if request.accept else "rejected"
    
    notif_use_case.execute(
        id_usuario=id_usuario,
        mensaje=mensaje,
        tipo=tipo,
        referencia_id=id_equipo,
        db=db
    )

    
    return {"message": "Solicitud procesada correctamente."}


@router.get("/{id_equipo}/share")
def share_team_redirect(id_equipo: int):
    """
    Endpoint web que redirige al detalle del equipo mediante deep link.
    """
    from fastapi.responses import HTMLResponse
    deep_link = f"matchday://app/team-dashboard/{id_equipo}"
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="0;url={deep_link}">
        <title>Redirigiendo a MatchDay...</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center;
                   align-items: center; height: 100vh; margin: 0; background-color: #111; color: #fff; }}
            .box {{ text-align: center; }}
            a {{ color: #00A859; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Abriendo el equipo en MatchDay...</h2>
            <p>Si no abre automáticamente, <a href="{deep_link}">presiona aquí</a>.</p>
        </div>
        <script>window.location.href = "{deep_link}";</script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


