from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.finance.infrastructure.bcv_service import BCVService

router = APIRouter(tags=["Finance"])

@router.get("/rates/latest")
def get_latest_rates(db: Session = Depends(get_db)):
    """
    Endpoint de Grado Industrial para consulta de tasas vigentes.
    Recupera las tasas USD/EUR del BCV persistidas localmente aplicando 
    filtros de fecha valor para cumplimiento normativo los fines de semana.
    """
    service = BCVService(db)
    rates = service.get_latest_rates()
    
    if not rates:
        raise HTTPException(
            status_code=503, 
            detail="Tasas de cambio no disponibles en este momento. Intente más tarde."
        )
        
    return rates