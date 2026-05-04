from app.core.exceptions import UnauthorizedException, ConflictException, MatchDayException

class InvalidGoogleTokenException(UnauthorizedException):
    """Excepción lanzada cuando el token de Google Sign-In es inválido o expiró."""
    def __init__(self, message: str = "El token de Google es inválido."):
        super().__init__(message)

class AuthException(MatchDayException):
    """Excepción genérica para problemas de autenticación."""
    def __init__(self, message: str, code: int = 400):
        super().__init__(message, code=code)

class EmailAlreadyExistsException(ConflictException):
    def __init__(self, message: str = "El correo electrónico ya está registrado."):
        super().__init__(message)

class InvalidCredentialsException(UnauthorizedException):
    def __init__(self, message: str = "Correo o contraseña incorrectos."):
        super().__init__(message)
