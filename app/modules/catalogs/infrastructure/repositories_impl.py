from typing import List
from sqlalchemy.orm import Session
from app.modules.catalogs.domain.entities import Deporte, Region, Cancha
from app.modules.catalogs.domain.interfaces import IDeporteRepository, IRegionRepository, ICanchaRepository
from app.modules.catalogs.infrastructure.orm_models import DeporteORM, RegionORM, CanchaORM

class DeporteRepositoryImpl(IDeporteRepository):
    """
    Implementación en base de datos del repositorio de Deportes.
    """
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Deporte]:
        """
        Consulta y devuelve todos los deportes almacenados en la base de datos.
        
        :return: Lista de entidades de dominio Deporte.
        """
        orms = self.db.query(DeporteORM).all()
        return [Deporte(id_deporte=orm.id_deporte, nombre_deporte=orm.nombre_deporte) for orm in orms]

class RegionRepositoryImpl(IRegionRepository):
    """
    Implementación en base de datos del repositorio de Regiones.
    """
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Region]:
        """
        Consulta y devuelve todas las regiones almacenadas en la base de datos.
        
        :return: Lista de entidades de dominio Region.
        """
        orms = self.db.query(RegionORM).all()
        return [Region(id_region=orm.id_region, nombre_region=orm.nombre_region, fk_id_region=orm.fk_id_region) for orm in orms]

class CanchaRepositoryImpl(ICanchaRepository):
    """
    Implementación en base de datos del repositorio de Canchas.
    """
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, region_id: int = None) -> List[Cancha]:
        """
        Consulta y devuelve las canchas, opcionalmente filtradas por región.
        
        :param region_id: ID de la región (opcional).
        :return: Lista de entidades de dominio Cancha.
        """
        query = self.db.query(CanchaORM)
        if region_id:
            query = query.filter(CanchaORM.fk_id_region == region_id)
        orms = query.all()
        return [Cancha(id_cancha=orm.id_cancha, nombre_cancha=orm.nombre_cancha, direccion_cancha=orm.direccion_cancha, fk_id_region=orm.fk_id_region) for orm in orms]
