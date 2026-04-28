from app.core.security import verify_google_token, create_access_token, get_password_hash, verify_password
from app.modules.auth.domain.interfaces import IUsuarioRepository
from app.modules.users.domain.entities import Usuario
from app.modules.auth.domain.exceptions import InvalidGoogleTokenException, EmailAlreadyExistsException, InvalidCredentialsException, AuthException
from typing import Optional

class GoogleLoginUseCase:
    """
    Caso de uso para iniciar sesión o registrarse con Google Sign-In.
    Orquesta la lógica entre el token de Google, la base de datos y nuestro JWT.
    """
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository

    def execute(self, id_token: str) -> str:
        """
        1. Valida el token de Google.
        2. Busca si el usuario existe.
        3. Si no existe, lo crea con el rol por defecto ('Jugador').
        4. Retorna el JWT propio de la aplicación.
        """
        try:
            # 1. Validar Token de Google
            google_user_info = verify_google_token(id_token)
        except ValueError as e:
            raise InvalidGoogleTokenException(str(e))

        email = google_user_info.get("email")
        name = google_user_info.get("name")
        picture = google_user_info.get("picture")

        if not email:
            raise InvalidGoogleTokenException("El token de Google no contiene un email válido.")

        # 2. Buscar usuario
        usuario = self.usuario_repository.get_by_email(email)

        # 3. Si no existe, lo creamos
        if not usuario:
            nuevo_usuario = Usuario(
                id_usuario=None,
                nombre_usuario=name or "Usuario Sin Nombre",
                email_usuario=email,
                password_hash=None,
                telefono_usuario=None,
                url_foto_perfil=picture,
                rol_usuario="Standard", # Valor por defecto acorde a la BD.
                reliability_score=5.00,
                fecha_creacion_usuario=None
            )

            usuario = self.usuario_repository.create(nuevo_usuario)

        # 4. Generar y retornar el JWT propio
        # Usamos sub para el ID del usuario, que es una convención estándar
        access_token = create_access_token(
            data={"sub": str(usuario.id_usuario), "email": usuario.email_usuario, "rol": usuario.rol_usuario}
        )
        
        return access_token

class RegisterUserUseCase:
    """
    Caso de uso para registrar un usuario de forma local con correo y contraseña.
    """
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository

    def execute(self, nombre_usuario: str, email: str, password: str, telefono: Optional[str] = None) -> str:
        # 1. Verificar si el correo ya existe
        usuario_existente = self.usuario_repository.get_by_email(email)
        if usuario_existente:
            raise EmailAlreadyExistsException()

        # 2. Encriptar contraseña
        hashed_password = get_password_hash(password)

        # 3. Crear Entidad
        nuevo_usuario = Usuario(
            id_usuario=None,
            nombre_usuario=nombre_usuario,
            email_usuario=email,
            password_hash=hashed_password,
            telefono_usuario=telefono,
            url_foto_perfil=None,
            rol_usuario="Standard",
            reliability_score=5.00,
            fecha_creacion_usuario=None
        )

        # 4. Guardar en BD
        usuario = self.usuario_repository.create(nuevo_usuario)

        # 5. Generar y retornar JWT
        access_token = create_access_token(
            data={"sub": str(usuario.id_usuario), "email": usuario.email_usuario, "rol": usuario.rol_usuario}
        )
        return access_token

class LoginUserUseCase:
    """
    Caso de uso para iniciar sesión localmente con correo y contraseña.
    """
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository

    def execute(self, email: str, password: str) -> str:
        # 1. Buscar al usuario
        usuario = self.usuario_repository.get_by_email(email)
        if not usuario:
            raise InvalidCredentialsException()

        # 2. Verificar contraseña (si no tiene, significa que usó Google)
        if not usuario.password_hash:
            raise AuthException("Este correo está registrado usando Google. Por favor, inicia sesión con Google.")

        if not verify_password(password, usuario.password_hash):
            raise InvalidCredentialsException()

        # 3. Generar y retornar JWT
        access_token = create_access_token(
            data={"sub": str(usuario.id_usuario), "email": usuario.email_usuario, "rol": usuario.rol_usuario}
        )
        return access_token

class RequestPasswordResetUseCase:
    """
    Caso de uso para solicitar el restablecimiento de contraseña.
    """
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository

    def execute(self, email: str) -> str:
        usuario = self.usuario_repository.get_by_email(email)
        if not usuario:
            # Por seguridad, no revelamos si el correo existe o no
            return None

        # Si el usuario existe pero no tiene contraseña, significa que es de Google
        # y no debería recuperar contraseña por aquí, sino iniciar con Google.
        if not usuario.password_hash:
            raise AuthException("Este correo está registrado usando Google. Por favor, inicia sesión con Google.")

        from app.core.security import create_password_reset_token
        token = create_password_reset_token(email)
        return token

class ResetPasswordUseCase:
    """
    Caso de uso para restablecer la contraseña usando un token.
    """
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository

    def execute(self, token: str, new_password: str) -> bool:
        from app.core.security import verify_password_reset_token, get_password_hash
        
        email = verify_password_reset_token(token)
        if not email:
            raise AuthException("El enlace de recuperación es inválido o ha expirado.")

        usuario = self.usuario_repository.get_by_email(email)
        if not usuario:
            raise AuthException("Usuario no encontrado.")

        usuario.password_hash = get_password_hash(new_password)
        self.usuario_repository.update(usuario)
        return True
