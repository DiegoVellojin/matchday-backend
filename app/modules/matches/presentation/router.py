from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.exceptions import NotFoundException, ConflictException, UnauthorizedException
from app.modules.matches.presentation.schemas import MatchCreateRequest, MatchResponse, ProposeTermsRequest, RegisterResultRequest
from app.modules.matches.application.use_cases import (
    CreateMatchUseCase, GetMatchesUseCase, GetMatchDetailsUseCase, 
    AcceptEncounterUseCase, ProposeTermsUseCase, JoinMatchUseCase,
    RegisterMatchResultUseCase
)
from app.modules.matches.infrastructure.repositories_impl import MatchRepositoryImpl

router = APIRouter(prefix="/matches", tags=["Matches"])

@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(
    request: MatchCreateRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repository = MatchRepositoryImpl(db)
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
    db: Session = Depends(get_db)
):
    repository = MatchRepositoryImpl(db)
    use_case = GetMatchesUseCase(repository)
    return use_case.execute(
        sport_id=sport_id, 
        status=status,
        region_id=region_id,
        cancha_id=cancha_id,
        fecha=fecha
    )

@router.get("/{match_id}", response_model=MatchResponse)
def get_match(
    match_id: int,
    db: Session = Depends(get_db)
):
    repository = MatchRepositoryImpl(db)
    use_case = GetMatchDetailsUseCase(repository)
    match = use_case.execute(match_id)
    if not match:
        raise NotFoundException("Partido no encontrado")
    return match

@router.post("/{match_id}/accept/{team_id}", response_model=MatchResponse)
def accept_match(
    match_id: int,
    team_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repository = MatchRepositoryImpl(db)
    use_case = AcceptEncounterUseCase(repository)
    # Aquí se podría validar que el usuario es el capitán del equipo_id
    return use_case.execute(match_id, team_id)

@router.post("/{match_id}/propose-terms", response_model=MatchResponse)
def propose_terms(
    match_id: int,
    request: ProposeTermsRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    repository = MatchRepositoryImpl(db)
    use_case = ProposeTermsUseCase(repository)
    
    return use_case.execute(
        match_id, 
        current_user_id, 
        request.fecha_acordada, 
        request.costo_total
    )

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
    return {"message": "Resultado registrado exitosamente"}
