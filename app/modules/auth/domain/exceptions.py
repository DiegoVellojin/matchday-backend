class InvalidGoogleTokenException(Exception):
    """Excepción lanzada cuando el token de Google Sign-In es inválido o expiró."""
    def __init__(self, message: str = "El token de Google es inválido."):
        self.message = message
        super().__init__(self.message)

class AuthException(Exception):
    """Excepción genérica para problemas de autenticación."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class EmailAlreadyExistsException(AuthException):
    def __init__(self, message: str = "El correo electrónico ya está registrado."):
        super().__init__(message)

class InvalidCredentialsException(AuthException):
    def __init__(self, message: str = "Correo o contraseña incorrectos."):
        super().__init__(message)
