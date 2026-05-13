from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.modules.teams.infrastructure.repositories_impl import TeamRepositoryImpl
from app.modules.teams.application.use_cases import CreateTeamUseCase, RequestJoinTeamUseCase, GetMyTeamsUseCase, JoinTeamWithTokenUseCase, GetPendingMembersUseCase, RespondToJoinRequestUseCase, GetDiscoverableTeamsUseCase, UpdateTeamUseCase, DeleteTeamUseCase, TransferCaptainUseCase

from app.modules.teams.presentation.schemas import TeamCreateRequest, TeamResponse, MemberResponse, RespondRequest, TeamUpdateRequest
from app.modules.matches.infrastructure.orm_models import PartidaORM
from sqlalchemy import or_

router = APIRouter()

@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    request: TeamCreateRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo equipo y asigna al usuario autenticado como Capitán.
    
    El proceso incluye la creación del registro del equipo y la inserción 
    automática del creador en la tabla de miembros con estatus 'aceptado'.
    """
    repo = TeamRepositoryImpl(db)
    use_case = CreateTeamUseCase(repo)
    
    equipo = use_case.execute(
        nombre=request.nombre_equipo,
        id_deporte=request.fk_id_deporte,
        id_usuario_creador=current_user_id,
        url_logo=request.url_logo_equipo,
        descripcion=request.descripcion_equipo,
        esta_reclutando=request.esta_reclutando,
        max_miembros=request.max_miembros,
        url_chat=request.url_chat_equipo
    )
    
    eq_dict = equipo.__dict__.copy()
    eq_dict["miembros_actuales"] = 1
    eq_dict["partidos_jugados"] = 0 # Recién creado siempre es 0
    return eq_dict


@router.get("/", response_model=List[TeamResponse])
def get_discoverable_teams(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Recupera el listado de equipos que tienen activada la opción de reclutamiento.
    
    Incluye metadatos adicionales como si el usuario actual ya es miembro 
    y el conteo de jugadores aceptados.
    """
    repo = TeamRepositoryImpl(db)
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
        
        # Calcular partidos jugados (completados)
        part_count = db.query(PartidaORM).filter(
            or_(
                PartidaORM.fk_id_equipo_a == eq.id_equipo,
                PartidaORM.fk_id_equipo_b == eq.id_equipo
            ),
            PartidaORM.estatus_partida == 'completada'
        ).count()
        
        eq_dict = eq.__dict__.copy()
        eq_dict["miembros_actuales"] = count if count > 0 else 1
        eq_dict["soy_miembro"] = es_miembro
        eq_dict["partidos_jugados"] = part_count
        response.append(eq_dict)
    return response


@router.get("/me", response_model=List[TeamResponse])
def get_my_teams(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Obtiene los equipos donde el usuario autenticado tiene una membresía activa.
    """
    repo = TeamRepositoryImpl(db)
    use_case = GetMyTeamsUseCase(repo)
    equipos = use_case.execute(id_usuario=current_user_id)
    
    from app.modules.teams.infrastructure.orm_models import EquipoUsuarioORM
    
    response = []
    for eq in equipos:
        count = db.query(EquipoUsuarioORM).filter(
            EquipoUsuarioORM.fk_id_equipo == eq.id_equipo,
            EquipoUsuarioORM.estatus_miembro == 'aceptado'
        ).count()
        # Calcular partidos jugados (completados)
        part_count = db.query(PartidaORM).filter(
            or_(
                PartidaORM.fk_id_equipo_a == eq.id_equipo,
                PartidaORM.fk_id_equipo_b == eq.id_equipo
            ),
            PartidaORM.estatus_partida == 'completada'
        ).count()
        
        eq_dict = eq.__dict__.copy()
        eq_dict["miembros_actuales"] = count if count > 0 else 1
        eq_dict["soy_miembro"] = True
        eq_dict["partidos_jugados"] = part_count
        response.append(eq_dict)
    return response


@router.get("/{id_equipo}", response_model=TeamResponse)
def get_team_detail(
    id_equipo: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna la información completa de un equipo específico identificado por su ID.
    """
    repo = TeamRepositoryImpl(db)
    equipo = repo.get_by_id(id_equipo)
    
    if not equipo:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Equipo no encontrado.")
        
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
    
    # Calcular partidos jugados (completados)
    partidos_count = db.query(PartidaORM).filter(
        or_(
            PartidaORM.fk_id_equipo_a == equipo.id_equipo,
            PartidaORM.fk_id_equipo_b == equipo.id_equipo
        ),
        PartidaORM.estatus_partida == 'completada'
    ).count()
    
    eq_dict = equipo.__dict__.copy()
    eq_dict["miembros_actuales"] = count if count > 0 else 1
    eq_dict["soy_miembro"] = es_miembro
    eq_dict["partidos_jugados"] = partidos_count
    return eq_dict


@router.post("/{id_equipo}/join", response_model=MemberResponse)
def join_team(
    id_equipo: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Inicia un proceso de unión a un equipo enviando una solicitud pendiente al capitán.
    """
    repo = TeamRepositoryImpl(db)
    use_case = RequestJoinTeamUseCase(repo)
    
    if not repo.get_by_id(id_equipo):
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Equipo no encontrado")
        
    resultado = use_case.execute(id_equipo=id_equipo, id_usuario=current_user_id)
    
    # Notificar al capitán de la nueva solicitud
    equipo = repo.get_by_id(id_equipo)
    if equipo and equipo.fk_id_usuario_capitan:
        from app.modules.notifications.infrastructure.repositories_impl import NotificationRepositoryImpl
        from app.modules.notifications.application.use_cases import CreateNotificationUseCase
        
        notif_repo = NotificationRepositoryImpl(db)
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


@router.get("/{id_equipo}/invite-token")
def get_invite_token(
    id_equipo: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Genera un token de acceso directo para invitar jugadores al equipo. 
    Requiere permisos de Capitán.
    """
    repo = TeamRepositoryImpl(db)
    equipo = repo.get_by_id(id_equipo)
    
    if not equipo:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Equipo no encontrado")
    
    if equipo.fk_id_usuario_capitan != current_user_id:
        from app.core.exceptions import UnauthorizedException
        raise UnauthorizedException("Solo el capitán puede generar invitaciones.")
    
    from app.core.security import create_team_invitation_token
    token = create_team_invitation_token(id_equipo)
    return {"invitation_token": token}

@router.delete("/{id_equipo}/members/{id_usuario}")
def kick_member(
    id_equipo: int,
    id_usuario: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Remueve forzosamente a un miembro del equipo. 
    Restringido al Capitán del equipo.
    """
    repo = TeamRepositoryImpl(db)
    equipo = repo.get_by_id(id_equipo)
    
    if not equipo:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Equipo no encontrado.")
        
    if equipo.fk_id_usuario_capitan != current_user_id:
        from app.core.exceptions import UnauthorizedException
        raise UnauthorizedException("No eres el capitán de este equipo.")
        
    if id_usuario == current_user_id:
        from app.core.exceptions import ConflictException
        raise ConflictException("No puedes expulsarte a ti mismo. Usa el endpoint de abandono.")

    from app.modules.teams.infrastructure.orm_models import EquipoUsuarioORM
    
    db.query(EquipoUsuarioORM).filter(
        EquipoUsuarioORM.fk_id_equipo == id_equipo,
        EquipoUsuarioORM.fk_id_usuario == id_usuario
    ).delete()
    db.commit()
    
    return {"message": "Miembro expulsado correctamente."}

@router.post("/join-with-token", response_model=MemberResponse)
def join_with_token(
    token: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Procesa un token de invitación para unir al usuario inmediatamente como miembro aceptado.
    """
    repo = TeamRepositoryImpl(db)
    use_case = JoinTeamWithTokenUseCase(repo)
    return use_case.execute(token=token, id_usuario=current_user_id)

@router.get("/{id_equipo}/requests", response_model=List[MemberResponse])
def get_pending_requests(
    id_equipo: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista todas las solicitudes de unión pendientes de aprobación para un equipo.
    """
    repo = TeamRepositoryImpl(db)
    equipo = repo.get_by_id(id_equipo)
    
    if not equipo or equipo.fk_id_usuario_capitan != current_user_id:
        from app.core.exceptions import UnauthorizedException
        raise UnauthorizedException("Acceso denegado.")
        
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
    Retorna el listado de miembros aceptados de un equipo, incluyendo información básica de perfil.
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
    Permite al capitán aceptar o rechazar una solicitud de unión. 
    Notifica al jugador sobre el resultado.
    """
    repo = TeamRepositoryImpl(db)
    equipo = repo.get_by_id(id_equipo)
    
    if not equipo or equipo.fk_id_usuario_capitan != current_user_id:
        from app.core.exceptions import UnauthorizedException
        raise UnauthorizedException("Acceso denegado.")
    
    use_case = RespondToJoinRequestUseCase(repo)
    success = use_case.execute(id_equipo, id_usuario, request.accept)
    
    if not success:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Solicitud no encontrada.")
        
    # Notificar al jugador sobre la decisión
    from app.modules.notifications.infrastructure.repositories_impl import NotificationRepositoryImpl
    from app.modules.notifications.application.use_cases import CreateNotificationUseCase
    
    notif_repo = NotificationRepositoryImpl(db)
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
    Genera una página de redirección (Deep Link) para compartir el equipo en redes sociales.
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


@router.put("/{id_equipo}", response_model=TeamResponse)
def update_team(
    id_equipo: int,
    request: TeamUpdateRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Actualiza la configuración y metadatos del equipo. Exclusivo para el Capitán.
    """
    repo = TeamRepositoryImpl(db)
    equipo = repo.get_by_id(id_equipo)
    if not equipo:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Equipo no encontrado.")
    
    if equipo.fk_id_usuario_capitan != current_user_id:
        from app.core.exceptions import UnauthorizedException
        raise UnauthorizedException("No eres el capitán de este equipo.")
    
    use_case = UpdateTeamUseCase(repo)
    updated = use_case.execute(id_equipo, request.model_dump(exclude_none=True))
    if not updated:
        from app.core.exceptions import ConflictException
        raise ConflictException("No se pudo actualizar el equipo.")
    
    from app.modules.teams.infrastructure.orm_models import EquipoUsuarioORM
    count = db.query(EquipoUsuarioORM).filter(
        EquipoUsuarioORM.fk_id_equipo == id_equipo,
        EquipoUsuarioORM.estatus_miembro == 'aceptado'
    ).count()
    
    # Calcular partidos jugados (completados)
    part_count = db.query(PartidaORM).filter(
        or_(
            PartidaORM.fk_id_equipo_a == id_equipo,
            PartidaORM.fk_id_equipo_b == id_equipo
        ),
        PartidaORM.estatus_partida == 'completada'
    ).count()
    
    res_dict = updated.__dict__.copy()
    res_dict["miembros_actuales"] = count
    res_dict["soy_miembro"] = True
    res_dict["partidos_jugados"] = part_count
    return res_dict

@router.put("/{id_equipo}/transfer-captain/{id_nuevo_capitan}")
def transfer_captain(
    id_equipo: int,
    id_nuevo_capitan: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Cede la capitanía del equipo a otro miembro aceptado. 
    Requiere que el actual capitán realice la petición.
    """
    repo = TeamRepositoryImpl(db)
    equipo = repo.get_by_id(id_equipo)
    if not equipo:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Equipo no encontrado.")
    
    if equipo.fk_id_usuario_capitan != current_user_id:
        from app.core.exceptions import UnauthorizedException
        raise UnauthorizedException("Solo el capitán puede transferir su rol.")
    
    members = repo.get_members(id_equipo)
    es_miembro = any(m.fk_id_usuario == id_nuevo_capitan and m.estatus_miembro == "aceptado" for m in members)
    if not es_miembro:
        from app.core.exceptions import ConflictException
        raise ConflictException("El nuevo capitán debe ser un miembro aceptado del equipo.")

    use_case = TransferCaptainUseCase(repo)
    if use_case.execute(id_equipo, id_nuevo_capitan):
        return {"message": "Capitanía transferida con éxito."}
    from app.core.exceptions import ConflictException
    raise ConflictException("No se pudo transferir la capitanía.")

@router.delete("/{id_equipo}/leave")
def leave_team(
    id_equipo: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Permite que el usuario actual abandone el equipo. 
    Los capitanes no pueden abandonar sin transferir su rol previamente.
    """
    repo = TeamRepositoryImpl(db)
    equipo = repo.get_by_id(id_equipo)
    if not equipo:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Equipo no encontrado.")
    
    if equipo.fk_id_usuario_capitan == current_user_id:
        from app.core.exceptions import ConflictException
        raise ConflictException("El capitán no puede salirse sin transferir su rol o eliminar el equipo.")

    if repo.delete_member(id_equipo, current_user_id):
        return {"message": "Has salido del equipo correctamente."}
    from app.core.exceptions import ConflictException
    raise ConflictException("No eres miembro de este equipo o no se pudo procesar.")

@router.delete("/{id_equipo}")
def delete_team(
    id_equipo: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Disuelve el equipo por completo. Acción irreversible y exclusiva del Capitán.
    """
    repo = TeamRepositoryImpl(db)
    equipo = repo.get_by_id(id_equipo)
    if not equipo:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Equipo no encontrado.")
    
    if equipo.fk_id_usuario_capitan != current_user_id:
        from app.core.exceptions import UnauthorizedException
        raise UnauthorizedException("Solo el capitán puede eliminar el equipo.")

    use_case = DeleteTeamUseCase(repo)
    if use_case.execute(id_equipo):
        return {"message": "Equipo eliminado con éxito."}
    from app.core.exceptions import ConflictException
    raise ConflictException("No se pudo eliminar el equipo.")
