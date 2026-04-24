import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "MatchDay API"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Aquí luego agregaremos el SECRET_KEY para los tokens JWT de Google
    # SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key")

settings = Settings()