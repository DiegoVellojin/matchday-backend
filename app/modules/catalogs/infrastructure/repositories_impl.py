from typing import List
from sqlalchemy.orm import Session
from app.modules.catalogs.domain.entities import Deporte, Region, Cancha
from app.modules.catalogs.domain.interfaces import IDeporteRepository, IRegionRepository, ICanchaRepository
from app.modules.catalogs.infrastructure.orm_models import DeporteORM, RegionORM, CanchaORM

class DeporteRepositoryImpl(IDeporteRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Deporte]:
        orms = self.db.query(DeporteORM).all()
        return [Deporte(id_deporte=orm.id_deporte, nombre_deporte=orm.nombre_deporte) for orm in orms]

class RegionRepositoryImpl(IRegionRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Region]:
        orms = self.db.query(RegionORM).all()
        return [Region(id_region=orm.id_region, nombre_region=orm.nombre_region, fk_id_region=orm.fk_id_region) for orm in orms]

class CanchaRepositoryImpl(ICanchaRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, region_id: int = None) -> List[Cancha]:
        query = self.db.query(CanchaORM)
        if region_id:
            query = query.filter(CanchaORM.fk_id_region == region_id)
        orms = query.all()
        return [Cancha(id_cancha=orm.id_cancha, nombre_cancha=orm.nombre_cancha, direccion_cancha=orm.direccion_cancha, fk_id_region=orm.fk_id_region) for orm in orms]
