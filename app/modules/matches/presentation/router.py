from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.modules.matches.presentation.schemas import MatchCreateRequest, MatchResponse, ProposeTermsRequest
from app.modules.matches.application.use_cases import (
    CreateMatchUseCase, GetMatchesUseCase, GetMatchDetailsUseCase, 
    AcceptEncounterUseCase, ProposeTermsUseCase, JoinMatchUseCase
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

@router.get("/", response_model=List[MatchResponse])
def list_matches(
    sport_id: Optional[int] = None,
    status: Optional[str] = "publicada",
    db: Session = Depends(get_db)
):
    repository = MatchRepositoryImpl(db)
    use_case = GetMatchesUseCase(repository)
    return use_case.execute(sport_id=sport_id, status=status)

@router.get("/{match_id}", response_model=MatchResponse)
def get_match(
    match_id: int,
    db: Session = Depends(get_db)
):
    repository = MatchRepositoryImpl(db)
    use_case = GetMatchDetailsUseCase(repository)
    match = use_case.execute(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
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
    try:
        return use_case.execute(
            match_id, 
            current_user_id, 
            request.fecha_acordada, 
            request.costo_total
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
        raise HTTPException(status_code=400, detail="No se pudo unir al partido")
    return {"message": "Te has unido al partido"}
