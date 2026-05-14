import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "MatchDay API"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 días de sesión
    
    # Google Auth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    
    # URL base del servidor (usada para construir links en correos)
    # En producción, configura BASE_URL=https://api.matchday.com en el .env
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")

    # Mail Settings (Resend API)
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    # Resend requiere usar 'onboarding@resend.dev' si no has verificado un dominio propio
    RESEND_FROM_EMAIL: str = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")

settings = Settings()