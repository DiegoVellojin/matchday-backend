from typing import List, Dict, Optional
from app.modules.payments.domain.interfaces import IPaymentRepository
from app.core.exceptions import UnauthorizedException, NotFoundException

class GetMyPaymentsUseCase:
    """Obtiene los pagos de un usuario específico."""
    def __init__(self, repository: IPaymentRepository):
        self.repository = repository

    def execute(self, user_id: int) -> List[Dict]:
        return self.repository.get_user_payments(user_id)


class UploadReceiptUseCase:
    """Registra o sube el reporte/comprobante de pago para una partida."""
    def __init__(self, repository: IPaymentRepository):
        self.repository = repository

    def execute(self, id_partida: int, user_id: int, url_recibo_pago: str, referencia_pago: str, tasa_usada_bs: Optional[float] = None) -> None:
        self.repository.upload_receipt(id_partida, user_id, url_recibo_pago, referencia_pago, tasa_usada_bs)


class GetTeamPaymentsToValidateUseCase:
    """Obtiene pagos del equipo para validación, asegurando que el usuario sea el capitán."""
    def __init__(self, repository: IPaymentRepository):
        self.repository = repository

    def execute(self, id_equipo: int, user_id: int) -> List[Dict]:
        if not self.repository.is_team_captain(id_equipo, user_id):
            raise UnauthorizedException("No eres el capitán de este equipo")
        
        return self.repository.get_team_payments(id_equipo)


class VerifyUserPaymentUseCase:
    """Verifica el pago de un usuario específico (Solo para capitanes)."""
    def __init__(self, repository: IPaymentRepository):
        self.repository = repository

    def execute(self, id_partida: int, id_usuario: int, current_user_id: int) -> None:
        if not self.repository.is_match_captain(id_partida, current_user_id):
            raise UnauthorizedException("No eres el capitán del equipo de esta partida")
            
        self.repository.verify_payment(id_partida, id_usuario)
