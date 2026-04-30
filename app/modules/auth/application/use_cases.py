from app.core.security import verify_google_token, create_access_token, get_password_hash, verify_password
from app.modules.auth.domain.interfaces import IUsuarioRepository
from app.modules.users.domain.entities import Usuario
from app.modules.auth.domain.exceptions import InvalidGoogleTokenException, EmailAlreadyExistsException, InvalidCredentialsException, AuthException
from typing import Optional

class GoogleLoginUseCase:
    """
    Caso de uso para el inicio de sesión o registro mediante Google Sign-In.
    
    Orquesta la validación del token de Google, la sincronización con el 
    repositorio de usuarios y la generación del token de acceso local (JWT).
    """
    
    def __init__(self, usuario_repository: IUsuarioRepository):
        """
        :param usuario_repository: Implementación del repositorio de usuarios.
        """
        self.usuario_repository = usuario_repository

    def execute(self, id_token: str) -> str:
        """
        Valida el token de Google y retorna un JWT de la aplicación.
        
        Si el usuario no existe en la base de datos local, se crea uno nuevo 
        automáticamente utilizando la información proporcionada por Google.
        
        :param id_token: El ID Token enviado desde el cliente de Google.
        :raises InvalidGoogleTokenException: Si el token de Google es inválido o no contiene email.
        :return: Token de acceso JWT firmado por MatchDay.
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
        access_token = create_access_token(
            data={"sub": str(usuario.id_usuario), "email": usuario.email_usuario, "rol": usuario.rol_usuario}
        )
        
        return access_token

class RegisterUserUseCase:
    """
    Caso de uso para el registro de nuevos usuarios mediante credenciales locales.
    """
    
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository

    def execute(self, nombre_usuario: str, email: str, password: str, telefono: Optional[str] = None) -> str:
        """
        Registra un usuario local y retorna su primer token de acceso.
        
        :param nombre_usuario: Nombre completo o alias del usuario.
        :param email: Correo electrónico único.
        :param password: Contraseña en texto plano (será hasheada).
        :param telefono: Número de contacto opcional.
        :raises EmailAlreadyExistsException: Si el correo ya está en uso.
        :return: Token de acceso JWT.
        """
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
    Caso de uso para la autenticación de usuarios mediante email y contraseña.
    """
    
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository

    def execute(self, email: str, password: str) -> str:
        """
        Valida las credenciales del usuario y genera un token JWT.
        
        :param email: Correo del usuario.
        :param password: Contraseña a verificar.
        :raises InvalidCredentialsException: Si el usuario no existe o la clave es incorrecta.
        :raises AuthException: Si el usuario fue creado vía Google.
        :return: Token de acceso JWT.
        """
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
    Caso de uso para iniciar el flujo de recuperación de cuenta.
    """
    
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository

    def execute(self, email: str) -> Optional[str]:
        """
        Genera un token de recuperación para el email proporcionado.
        
        :param email: Correo que solicita el reset.
        :raises AuthException: Si la cuenta está vinculada a Google.
        :return: Token de reset o None si el usuario no existe (seguridad).
        """
        usuario = self.usuario_repository.get_by_email(email)
        if not usuario:
            return None

        if not usuario.password_hash:
            raise AuthException("Este correo está registrado usando Google. Por favor, inicia sesión con Google.")

        from app.core.security import create_password_reset_token
        token = create_password_reset_token(email)
        return token

class ResetPasswordUseCase:
    """
    Caso de uso para aplicar la nueva contraseña tras validar un token de recuperación.
    """
    
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository

    def execute(self, token: str, new_password: str) -> bool:
        """
        Valida el token y actualiza la contraseña del usuario asociado.
        
        :param token: Token de recuperación recibido por el usuario.
        :param new_password: Nueva contraseña a establecer.
        :raises AuthException: Si el token es inválido o el usuario no existe.
        :return: True si la actualización fue exitosa.
        """
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
