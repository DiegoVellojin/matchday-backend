from abc import ABC, abstractmethod
from typing import List, Optional
from app.modules.catalogs.domain.entities import Deporte, Region, Cancha

class ISportRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Deporte]:
        pass

class IRegionRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Region]:
        pass

class ICourtRepository(ABC):
    @abstractmethod
    def get_all(self, region_id: Optional[int] = None) -> List[Cancha]:
        pass

    @abstractmethod
    def create(self, cancha_data: dict) -> Cancha:
        pass
