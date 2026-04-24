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
