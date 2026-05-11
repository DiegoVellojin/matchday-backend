from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.modules.auth.presentation.schemas import GoogleAuthRequest, AuthResponse, RegisterRequest, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.modules.auth.application.use_cases import GoogleLoginUseCase, RegisterUserUseCase, LoginUserUseCase, RequestPasswordResetUseCase, ResetPasswordUseCase
from app.modules.auth.infrastructure.repositories_impl import UserRepositoryImpl
from app.modules.auth.domain.exceptions import InvalidGoogleTokenException, EmailAlreadyExistsException, InvalidCredentialsException, AuthException

router = APIRouter()

@router.post("/google", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def google_login(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Endpoint para autenticar a un usuario con Google Sign-In.
    """
    usuario_repo = UserRepositoryImpl(db)
    use_case = GoogleLoginUseCase(usuario_repository=usuario_repo)
    token = use_case.execute(id_token=request.id_token)
    return AuthResponse(access_token=token)

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Endpoint para registrar un nuevo usuario con correo y contraseña.
    """
    usuario_repo = UserRepositoryImpl(db)
    use_case = RegisterUserUseCase(usuario_repository=usuario_repo)
    token = use_case.execute(
        nombre_usuario=request.nombre_usuario,
        email=request.email,
        password=request.password,
        telefono=request.telefono
    )
    return AuthResponse(access_token=token)

@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Endpoint para iniciar sesión con correo y contraseña.
    """
    usuario_repo = UserRepositoryImpl(db)
    use_case = LoginUserUseCase(usuario_repository=usuario_repo)
    token = use_case.execute(email=request.email, password=request.password)
    return AuthResponse(access_token=token)

@router.get("/reset-password-redirect")
def reset_password_redirect(token: str):
    """
    Endpoint web que recibe el token y redirige a la app mediante deep link.
    Los clientes de correo (Gmail, Outlook) bloquean custom URI schemes directos,
    pero sí permiten abrir un link https:// que luego haga la redirección.
    """
    from fastapi.responses import HTMLResponse
    deep_link = f"matchday://app/reset-password?token={token}"
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="0;url={deep_link}">
        <title>Redirigiendo a MatchDay...</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center;
                   align-items: center; height: 100vh; margin: 0; background-color: #111; color: #fff; }}
            .box {{ text-align: center; }}
            a {{ color: #00A859; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Abriendo MatchDay...</h2>
            <p>Si no abre automáticamente, <a href="{deep_link}">presiona aquí</a>.</p>
        </div>
        <script>window.location.href = "{deep_link}";</script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Endpoint para solicitar la recuperación de contraseña.
    """
    usuario_repo = UserRepositoryImpl(db)
    use_case = RequestPasswordResetUseCase(usuario_repository=usuario_repo)
    
    token = use_case.execute(email=request.email)
    if token:
        from app.core.mail import send_password_reset_email
        from app.core.config import settings

        # Obtener el nombre del usuario para personalizar el saludo
        usuario = usuario_repo.get_by_email(request.email)
        nombre = usuario.nombre_usuario if usuario else "Jugador"

        reset_link = f"{settings.BASE_URL}/api/v1/auth/reset-password-redirect?token={token}"
        background_tasks.add_task(send_password_reset_email, request.email, reset_link, nombre)
    
    return {"message": "Si el correo está registrado, recibirás un enlace para restablecer tu contraseña."}

@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Endpoint para restablecer la contraseña usando el token temporal.
    """
    usuario_repo = UserRepositoryImpl(db)
    use_case = ResetPasswordUseCase(usuario_repository=usuario_repo)
    use_case.execute(token=request.token, new_password=request.new_password)
    return {"message": "Contraseña actualizada exitosamente."}
