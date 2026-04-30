from typing import List
from app.modules.catalogs.domain.entities import Deporte, Region, Cancha
from app.modules.catalogs.domain.interfaces import IDeporteRepository, IRegionRepository, ICanchaRepository

class GetSportsUseCase:
    def __init__(self, repository: IDeporteRepository):
        self.repository = repository

    def execute(self) -> List[Deporte]:
        return self.repository.get_all()

class GetRegionsUseCase:
    def __init__(self, repository: IRegionRepository):
        self.repository = repository

    def execute(self) -> List[Region]:
        return self.repository.get_all()

class GetCanchasUseCase:
    def __init__(self, repository: ICanchaRepository):
        self.repository = repository

    def execute(self, region_id: int = None) -> List[Cancha]:
        return self.repository.get_all(region_id=region_id)
