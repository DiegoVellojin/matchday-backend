from typing import List, Optional
from app.modules.catalogs.domain.entities import Deporte, Region, Cancha
from app.modules.catalogs.domain.interfaces import ISportRepository, IRegionRepository, ICourtRepository

class GetSportsUseCase:
    """
    Caso de uso para obtener todos los deportes disponibles.
    """
    def __init__(self, repository: ISportRepository):
        self.repository = repository

    def execute(self) -> List[Deporte]:
        """
        Ejecuta la obtención de la lista completa de deportes.
        
        :return: Lista de entidades Deporte.
        """
        return self.repository.get_all()

class GetRegionsUseCase:
    """
    Caso de uso para obtener todas las regiones geográficas.
    """
    def __init__(self, repository: IRegionRepository):
        self.repository = repository

    def execute(self) -> List[Region]:
        """
        Ejecuta la obtención de la lista completa de regiones.
        
        :return: Lista de entidades Region.
        """
        return self.repository.get_all()

class GetCanchasUseCase:
    """
    Caso de uso para obtener las canchas, opcionalmente filtradas por región.
    """
    def __init__(self, repository: ICourtRepository):
        self.repository = repository

    def execute(self, region_id: Optional[int] = None) -> List[Cancha]:
        """
        Ejecuta la consulta de canchas.
        
        :param region_id: (Opcional) ID de la región para filtrar los resultados.
        :return: Lista de entidades Cancha.
        """
        return self.repository.get_all(region_id=region_id)

class CreateCanchaUseCase:
    """
    Caso de uso para insertar una nueva cancha.
    """
    def __init__(self, repository: ICourtRepository):
        self.repository = repository

    def execute(self, cancha_data: dict) -> Cancha:
        """
        Ejecuta la creación de una cancha.
        
        :param cancha_data: Datos de la cancha a crear.
        :return: Entidad Cancha creada.
        """
        return self.repository.create(cancha_data)
