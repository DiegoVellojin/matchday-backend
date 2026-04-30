from abc import ABC, abstractmethod
from typing import List
from app.modules.catalogs.domain.entities import Deporte, Region, Cancha

class IDeporteRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Deporte]:
        pass

class IRegionRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Region]:
        pass

class ICanchaRepository(ABC):
    @abstractmethod
    def get_all(self, region_id: int = None) -> List[Cancha]:
        pass
