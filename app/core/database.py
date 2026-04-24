import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# 1. Cargar las variables de entorno desde el archivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("⚠️ CRÍTICO: La variable DATABASE_URL no está configurada en el archivo .env")

# 2. Configurar el Engine (El motor de conexión)
# pool_pre_ping=True verifica que la conexión esté viva antes de usarla (ideal para Neon que es serverless)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 3. Configurar la fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Clase base para nuestros modelos ORM
Base = declarative_base()

# 5. Dependencia de FastAPI (Dependency Injection)
# Esto garantiza que cada petición HTTP tenga su propia sesión de BD aislada y la cierre al terminar.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()