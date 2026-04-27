from abc import ABC, abstractmethod
from typing import List
from app.modules.catalogs.domain.entities import Deporte

class IDeporteRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Deporte]:
        pass
