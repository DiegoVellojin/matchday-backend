from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user_id, get_optional_user_id
from app.core.exceptions import NotFoundException, ConflictException, UnauthorizedException
from app.modules.matches.presentation.schemas import MatchCreateRequest, MatchResponse, ProposeTermsRequest, RegisterResultRequest, MatchConfigureRequest, MatchPlayerResponse
from app.modules.matches.application.use_cases import (
    CreateMatchUseCase, GetMatchesUseCase, GetMatchDetailsUseCase,
    AcceptEncounterUseCase, ProposeTermsUseCase, ConfigureMatchUseCase,
    JoinMatchUseCase, RegisterMatchResultUseCase, MarkTeamReadyUseCase,
    GetMatchPlayersUseCase
)
from app.modules.matches.infrastructure.repositories_impl import MatchRepositoryImpl
from app.modules.notifications.infrastructure.repositories_impl import NotificationRepositoryImpl
from app.modules.notifications.application.use_cases import CreateNotificationUseCase

router = APIRouter(prefix="/matches", tags=["Matches"])

@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(
    request: MatchCreateRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repository = MatchRepositoryImpl(db)
    
    # Validar que el usuario es capitán del equipo A
    if request.fk_id_equipo_a:
        from app.modules.teams.infrastructure.repositories_impl import TeamRepositoryImpl
        team_repo = TeamRepositoryImpl(db)
        team = team_repo.get_by_id(request.fk_id_equipo_a)
        if not team or team.fk_id_usuario_capitan != current_user_id:
            raise UnauthorizedException("Solo el capitán del equipo puede solicitar un encuentro")

    use_case = CreateMatchUseCase(repository)
    match_data = request.model_dump()
    match_data["fk_id_usuario_org"] = current_user_id
    
    return use_case.execute(match_data)

from datetime import datetime
 
@router.get("/", response_model=List[MatchResponse])
def list_matches(
    sport_id: Optional[int] = None,
    status: Optional[str] = "publicada",
    region_id: Optional[int] = None,
    cancha_id: Optional[int] = None,
    fecha: Optional[datetime] = None,
    mine: bool = False,
    team_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = Depends(get_optional_user_id)
):
    repository = MatchRepositoryImpl(db)
    use_case = GetMatchesUseCase(repository)
    
    if mine and not current_user_id:
        raise UnauthorizedException("Debe iniciar sesión para ver sus partidos")
    
    # Si busca sus propios partidos o de un equipo, omitimos el filtro de status "publicada" por defecto
    # para que vea los que están en negociación, pendientes de pago, completados (historial), etc.
    final_status = status
    final_user_id = None
    final_exclude_user_id = None
    
    if (mine and current_user_id) or team_id:
        # Si no se pasó un status específico, buscamos todos los estados
        if status == "publicada":
            final_status = None
            
    if mine and current_user_id:
        final_user_id = current_user_id
    elif not mine and current_user_id and not team_id:
        final_exclude_user_id = current_user_id
            
    return use_case.execute(
        sport_id=sport_id, 
        status=final_status,
        region_id=region_id,
        cancha_id=cancha_id,
        fecha=fecha,
        user_id=final_user_id,
        team_id=team_id,
        exclude_user_id=final_exclude_user_id
    )

@router.get("/{match_id}", response_model=MatchResponse)
def get_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = Depends(get_optional_user_id)
):
    repository = MatchRepositoryImpl(db)
    use_case = GetMatchDetailsUseCase(repository)
    match = use_case.execute(match_id)
    
    # Si el partido está completado, verificar evaluaciones
    if match.estatus_partida == 'completada':
        from app.modules.rankings.infrastructure.repositories_impl import RankingRepositoryImpl
        from app.modules.rankings.infrastructure.orm_models import EvaluacionORM
        ranking_repo = RankingRepositoryImpl(db)
        
        if current_user_id:
            match.ya_evaluado = ranking_repo.has_evaluated(match_id, current_user_id)
        
        # Obtener todas las evaluaciones del partido para mostrarlas públicamente
        evaluaciones_orm = db.query(EvaluacionORM).filter(EvaluacionORM.fk_id_partida == match_id).all()
        match.evaluaciones = [
            {
                "id_evaluacion": ev.id_evaluacion,
                "puntuacion": ev.puntuacion,
                "comentario": ev.comentario,
                "evaluador_nombre": ev.evaluador.nombre_usuario if ev.evaluador else "Usuario",
                "fecha_evaluacion": ev.fecha_evaluacion
            } for ev in evaluaciones_orm
        ]
        
    return match

@router.post("/{match_id}/accept/{team_id}", response_model=MatchResponse)
def accept_match(
    match_id: int,
    team_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repository = MatchRepositoryImpl(db)
    
    # Validar que el usuario es capitán del equipo que acepta
    from app.modules.teams.infrastructure.repositories_impl import TeamRepositoryImpl
    team_repo = TeamRepositoryImpl(db)
    team = team_repo.get_by_id(team_id)
    if not team or team.fk_id_usuario_capitan != current_user_id:
        raise UnauthorizedException("Solo el capitán del equipo puede aceptar un encuentro")

    use_case = AcceptEncounterUseCase(repository)
    match = use_case.execute(match_id, team_id)
    
    # Enviar notificación FCM al organizador (Capitán A)
    try:
        notif_repo = NotificationRepositoryImpl(db)
        notif_use_case = CreateNotificationUseCase(notif_repo)
        assert match.id is not None
        assert match.id is not None
        notif_use_case.execute(
            id_usuario=match.fk_id_usuario_org,
            mensaje=f"¡El equipo rival ha aceptado el reto! Entra a configurar los detalles del partido.",
            tipo="match_accepted",
            referencia_id=match.id,
            db=db
        )
    except Exception as e:
        print(f"Error al enviar notificación FCM en accept_match: {e}")
        
    return match

@router.post("/{match_id}/propose-terms", response_model=MatchResponse)
def propose_terms(
    match_id: int,
    request: ProposeTermsRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repository = MatchRepositoryImpl(db)
    use_case = ProposeTermsUseCase(repository)
    
    match = use_case.execute(
        match_id=match_id,
        user_id=current_user_id,
        fecha=request.fecha_acordada,
        costo=request.costo_total,
        moneda=request.moneda
    )
    
    # Notificar al otro capitán sobre la nueva propuesta
    try:
        target_user = match.fk_id_usuario_org if current_user_id != match.fk_id_usuario_org else None
        if target_user is None and match.fk_id_equipo_b:
             from app.modules.teams.infrastructure.repositories_impl import TeamRepositoryImpl
             team_repo = TeamRepositoryImpl(db)
             equipo_b = team_repo.get_by_id(match.fk_id_equipo_b)
             if equipo_b:
                 target_user = equipo_b.fk_id_usuario_capitan
        
        if target_user:
            notif_repo = NotificationRepositoryImpl(db)
            notif_use_case = CreateNotificationUseCase(notif_repo)
            notif_use_case.execute(
                id_usuario=target_user,
                mensaje=f"El capitán rival ha propuesto nuevos términos para el partido. ¡Revísalos!",
                tipo="terms_proposed",
                referencia_id=match_id,
                db=db
            )
    except Exception as e:
        print(f"Error al enviar notificación en propose_terms: {e}")
        
    return match

@router.put("/{match_id}/configure", response_model=MatchResponse)
def configure_match(
    match_id: int,
    request: MatchConfigureRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repository = MatchRepositoryImpl(db)
    use_case = ConfigureMatchUseCase(repository)
    
    match = use_case.execute(
        match_id=match_id, 
        user_id=current_user_id, 
        fecha=request.fecha_acordada, 
        costo=request.costo_total_partida,
        moneda=request.moneda,
        banco=request.banco_receptor,
        cedula=request.cedula_receptor,
        telefono=request.telefono_receptor
    )
    
    # Notificar a los jugadores si pasó a pendiente_pago (ambos configuraron o uno aceptó configuración)
    if match.estatus_partida == 'pendiente_pago':
        try:
            notif_repo = NotificationRepositoryImpl(db)
            notif_use_case = CreateNotificationUseCase(notif_repo)
            players = repository.get_players(match_id)
            for player in players:
                # Omitir al capitan (current_user_id o fk_id_usuario_org si ya pagó su parte)
                if player["id_usuario"] != current_user_id:
                    assert match.id is not None
                    assert match.id is not None
                    notif_use_case.execute(
                        id_usuario=player["id_usuario"],
                        mensaje=f"¡El partido está listo! Ya puedes realizar el pago de tu cuota al capitán.",
                        tipo="match_ready_to_pay",
                        referencia_id=match.id,
                        db=db
                    )
        except Exception as e:
            print(f"Error al enviar notificación en configure_match: {e}")
            
    return match

@router.post("/{match_id}/ready", response_model=MatchResponse)
def mark_team_ready(
    match_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repository = MatchRepositoryImpl(db)
    use_case = MarkTeamReadyUseCase(repository)
    match = use_case.execute(match_id, current_user_id)
    
    if match.estatus_partida == 'confirmada':
        # Notificar a todos que el partido está confirmado
        try:
            notif_repo = NotificationRepositoryImpl(db)
            notif_use_case = CreateNotificationUseCase(notif_repo)
            players = repository.get_players(match_id)
            for player in players:
                notif_use_case.execute(
                    id_usuario=player["id_usuario"],
                    mensaje=f"¡Luz verde! El partido ha sido confirmado y ambos equipos están listos.",
                    tipo="match_confirmed",
                    referencia_id=match.id,
                    db=db
                )
        except Exception:
            pass

    return match

@router.get("/{match_id}/players", response_model=List[MatchPlayerResponse])
def get_match_players(
    match_id: int,
    db: Session = Depends(get_db)
):
    repository = MatchRepositoryImpl(db)
    use_case = GetMatchPlayersUseCase(repository)
    return use_case.execute(match_id)

@router.post("/{match_id}/join")
def join_match(
    match_id: int,
    team_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repository = MatchRepositoryImpl(db)
    use_case = JoinMatchUseCase(repository)
    success = use_case.execute(match_id, current_user_id, team_id)
    if not success:
        raise ConflictException("No se pudo unir al partido")
    return {"message": "Te has unido al partido"}

@router.post("/{match_id}/results", status_code=status.HTTP_201_CREATED)
def register_result(
    match_id: int,
    request: RegisterResultRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repository = MatchRepositoryImpl(db)
    use_case = RegisterMatchResultUseCase(repository)
    use_case.execute(match_id, current_user_id, request.goles_a, request.goles_b)
    
    # Notificar al otro capitán para que confirme o ingrese sus resultados
    try:
        match = repository.get_by_id(match_id)
        if match:
            # Si el usuario actual es el org, notificamos al capitán B, sino al revés
            cap_b = None
            # Buscamos quién es el capitán B (el organizador del equipo B)
            if match.fk_id_equipo_b:
                from app.modules.teams.infrastructure.repositories_impl import TeamRepositoryImpl
                team_repo = TeamRepositoryImpl(db)
                equipo_b = team_repo.get_by_id(match.fk_id_equipo_b)
                if equipo_b:
                    cap_b = equipo_b.fk_id_usuario_capitan
            
            target_user = cap_b if current_user_id == match.fk_id_usuario_org else match.fk_id_usuario_org
            
            if target_user:
                notif_repo = NotificationRepositoryImpl(db)
                notif_use_case = CreateNotificationUseCase(notif_repo)
                notif_use_case.execute(
                    id_usuario=target_user,
                    mensaje=f"El equipo rival ha registrado un resultado ({request.goles_a}-{request.goles_b}). Por favor regístralo también para confirmarlo.",
                    tipo="result_registered",
                    referencia_id=match_id,
                    db=db
                )
    except Exception as e:
        print(f"Error al enviar notificación FCM en register_result: {e}")
        
    return {"message": "Resultado registrado exitosamente"}

@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repository = MatchRepositoryImpl(db)
    match = repository.get_by_id(match_id)
    if not match:
        raise NotFoundException("Partido no encontrado")
    
    if match.fk_id_usuario_org != current_user_id:
        raise UnauthorizedException("Solo el organizador puede cancelar este partido")
        
    # Solo permitir cancelar si está en 'publicada' o 'negociando' (antes de pagos)
    if match.estatus_partida not in ['publicada', 'negociando']:
        raise ConflictException("No se puede cancelar un partido en este estado")
        
    repository.delete(match_id)
    return None

@router.put("/{match_id}", status_code=status.HTTP_200_OK, response_model=MatchResponse)
def update_match(
    match_id: int,
    request: MatchCreateRequest, # Reutilizamos el esquema de creación para actualización básica
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repository = MatchRepositoryImpl(db)
    match = repository.get_by_id(match_id)
    if not match:
        raise NotFoundException("Partido no encontrado")
    
    if match.fk_id_usuario_org != current_user_id:
        raise UnauthorizedException("Solo el organizador puede editar este partido")
        
    # Solo permitir editar si está en 'publicada'
    if match.estatus_partida != 'publicada':
        raise ConflictException("No se puede editar un partido que ya está en negociación o pago")
        
    # Validar que el usuario es capitán del nuevo equipo A (si cambia)
    if request.fk_id_equipo_a is not None and request.fk_id_equipo_a != match.fk_id_equipo_a:
        from app.modules.teams.infrastructure.repositories_impl import TeamRepositoryImpl
        team_repo = TeamRepositoryImpl(db)
        team = team_repo.get_by_id(request.fk_id_equipo_a)
        if not team or team.fk_id_usuario_capitan != current_user_id:
            raise UnauthorizedException("Solo el capitán del equipo puede asignar su equipo a un encuentro")

    match.fk_id_deporte = request.fk_id_deporte
    match.fk_id_cancha = request.fk_id_cancha
    match.fecha_inicio_estimada = request.fecha_inicio_estimada
    match.fecha_fin_estimada = request.fecha_fin_estimada
    match.fk_id_equipo_a = request.fk_id_equipo_a
    
    updated_match = repository.update(match_id, request.model_dump())
    return updated_match
