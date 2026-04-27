from typing import List
from sqlalchemy.orm import Session
from app.modules.catalogs.domain.entities import Deporte
from app.modules.catalogs.domain.interfaces import IDeporteRepository
from app.modules.catalogs.infrastructure.orm_models import DeporteORM

class DeporteRepositoryImpl(IDeporteRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Deporte]:
        orms = self.db.query(DeporteORM).all()
        return [Deporte(id_deporte=orm.id_deporte, nombre_deporte=orm.nombre_deporte) for orm in orms]
