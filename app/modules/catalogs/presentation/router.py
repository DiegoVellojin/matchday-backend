from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.modules.catalogs.infrastructure.repositories_impl import DeporteRepositoryImpl, RegionRepositoryImpl, CanchaRepositoryImpl
from app.modules.catalogs.application.use_cases import GetSportsUseCase, GetRegionsUseCase, GetCanchasUseCase
from app.modules.catalogs.presentation.schemas import DeporteResponse, RegionResponse, CanchaResponse

router = APIRouter()

@router.get("/sports", response_model=List[DeporteResponse])
def get_sports(db: Session = Depends(get_db)):
    """
    Obtiene la lista de todos los deportes disponibles.
    """
    repo = DeporteRepositoryImpl(db)
    use_case = GetSportsUseCase(repo)
    return use_case.execute()

@router.get("/regions", response_model=List[RegionResponse])
def get_regions(db: Session = Depends(get_db)):
    """Obtiene la lista de todas las regiones/ciudades."""
    repo = RegionRepositoryImpl(db)
    use_case = GetRegionsUseCase(repo)
    return use_case.execute()

@router.get("/canchas", response_model=List[CanchaResponse])
def get_canchas(
    region_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Obtiene la lista de canchas, opcionalmente filtradas por región."""
    repo = CanchaRepositoryImpl(db)
    use_case = GetCanchasUseCase(repo)
    return use_case.execute(region_id=region_id)
