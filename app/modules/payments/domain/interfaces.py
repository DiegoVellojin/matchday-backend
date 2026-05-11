from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class IPaymentRepository(ABC):
    @abstractmethod
    def get_user_payments(self, user_id: int) -> List[Dict]:
        pass

    @abstractmethod
    def upload_receipt(self, id_partida: int, user_id: int, url_recibo_pago: str, referencia_pago: str) -> None:
        pass

    @abstractmethod
    def is_team_captain(self, id_equipo: int, user_id: int) -> bool:
        pass

    @abstractmethod
    def is_match_captain(self, id_partida: int, user_id: int) -> bool:
        pass

    @abstractmethod
    def get_team_payments(self, id_equipo: int) -> List[Dict]:
        pass

    @abstractmethod
    def verify_payment(self, id_partida: int, id_usuario: int) -> None:
        pass

    @abstractmethod
    def get_payment_captain(self, id_partida: int, user_id: int) -> Optional[int]:
        pass
