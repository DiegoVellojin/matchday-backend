from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.modules.catalogs.infrastructure.repositories_impl import DeporteRepositoryImpl
from app.modules.catalogs.application.use_cases import GetSportsUseCase
from app.modules.catalogs.presentation.schemas import DeporteResponse

router = APIRouter()

@router.get("/sports", response_model=List[DeporteResponse])
def get_sports(db: Session = Depends(get_db)):
    """
    Obtiene la lista de todos los deportes disponibles.
    """
    repo = DeporteRepositoryImpl(db)
    use_case = GetSportsUseCase(repo)
    return use_case.execute()
