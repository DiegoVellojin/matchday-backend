from app.core.security import verify_google_token, create_access_token
from app.modules.auth.domain.interfaces import IUsuarioRepository
from app.modules.auth.domain.entities import Usuario
from app.modules.auth.domain.exceptions import InvalidGoogleTokenException

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
                telefono_usuario=None,
                url_foto_perfil=picture,
                rol_usuario="Jugador", # Valor por defecto. Se limitará por la BD.
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
