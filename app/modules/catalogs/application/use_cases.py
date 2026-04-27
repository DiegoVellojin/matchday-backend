from typing import List
from app.modules.catalogs.domain.entities import Deporte
from app.modules.catalogs.domain.interfaces import IDeporteRepository

class GetSportsUseCase:
    def __init__(self, repository: IDeporteRepository):
        self.repository = repository

    def execute(self) -> List[Deporte]:
        return self.repository.get_all()
