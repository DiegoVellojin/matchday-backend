from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """
    Esquema genérico para respuestas paginadas.
    """
    total: int
    page: int
    size: int
    items: List[T]

class ErrorResponse(BaseModel):
    """
    Esquema estándar para respuestas de error (usado por el manejador global).
    """
    detail: str
    code: Optional[str] = None
