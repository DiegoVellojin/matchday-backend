from fastapi import HTTPException

class MatchDayException(Exception):
    """Excepción base para todos los errores de dominio de MatchDay."""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)

class NotFoundException(MatchDayException):
    def __init__(self, message: str = "Recurso no encontrado"):
        super().__init__(message, code=404)

class ConflictException(MatchDayException):
    def __init__(self, message: str = "Conflicto en la operación"):
        super().__init__(message, code=409)

class UnauthorizedException(MatchDayException):
    def __init__(self, message: str = "No autorizado"):
        super().__init__(message, code=401)

class ForbiddenException(MatchDayException):
    def __init__(self, message: str = "Prohibido"):
        super().__init__(message, code=403)
