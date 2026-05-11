from typing import List, Optional, cast
from sqlalchemy.orm import Session
from app.modules.catalogs.domain.entities import Deporte, Region, Cancha
from app.modules.catalogs.domain.interfaces import ISportRepository, IRegionRepository, ICourtRepository
from app.modules.catalogs.infrastructure.orm_models import DeporteORM, RegionORM, CanchaORM

class SportRepositoryImpl(ISportRepository):
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
        return [Deporte(id_deporte=cast(int, orm.id_deporte), nombre_deporte=cast(str, orm.nombre_deporte)) for orm in orms]

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
        return [Region(
            id_region=cast(int, orm.id_region),
            nombre_region=cast(str, orm.nombre_region),
            fk_id_region=cast(Optional[int], orm.fk_id_region)
        ) for orm in orms]

class CourtRepositoryImpl(ICourtRepository):
    """
    Implementación en base de datos del repositorio de Canchas.
    """
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, region_id: Optional[int] = None) -> List[Cancha]:
        """
        Consulta y devuelve las canchas, opcionalmente filtradas por región.
        
        :param region_id: ID de la región (opcional).
        :return: Lista de entidades de dominio Cancha.
        """
        query = self.db.query(CanchaORM)
        if region_id is not None:
            query = query.filter(CanchaORM.fk_id_region == region_id)
        orms = query.all()
        return [Cancha(
            id_cancha=cast(int, orm.id_cancha),
            nombre_cancha=cast(str, orm.nombre_cancha),
            direccion_cancha=cast(Optional[str], orm.direccion_cancha),
            fk_id_region=cast(int, orm.fk_id_region),
            latitud_cancha=cast(Optional[float], orm.latitud_cancha),
            longitud_cancha=cast(Optional[float], orm.longitud_cancha)
        ) for orm in orms]

    def create(self, cancha_data: dict) -> Cancha:
        """
        Inserta una nueva cancha en la base de datos.
        
        :param cancha_data: Diccionario con los datos de la cancha.
        :return: Entidad de dominio Cancha creada.
        """
        nueva_cancha = CanchaORM(**cancha_data)
        self.db.add(nueva_cancha)
        self.db.commit()
        self.db.refresh(nueva_cancha)
        return Cancha(
            id_cancha=cast(int, nueva_cancha.id_cancha),
            nombre_cancha=cast(str, nueva_cancha.nombre_cancha),
            direccion_cancha=cast(Optional[str], nueva_cancha.direccion_cancha),
            fk_id_region=cast(int, nueva_cancha.fk_id_region),
            latitud_cancha=cast(Optional[float], nueva_cancha.latitud_cancha),
            longitud_cancha=cast(Optional[float], nueva_cancha.longitud_cancha)
        )
