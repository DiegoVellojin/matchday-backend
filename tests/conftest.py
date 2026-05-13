import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.modules.catalogs.infrastructure.orm_models import DeporteORM, CanchaORM, RegionORM

# Configuración de la base de datos de pruebas (SQLite en memoria)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    execution_options={"schema_translate_map": {"bd_matchday": None}}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

@pytest.fixture(scope="function")
def db_session():
    """Crea una base de datos limpia y con catálogos base para cada test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Sembrar catálogos base
    padel = DeporteORM(id_deporte=1, nombre_deporte="Padel", max_jugadores_deporte=4)
    region = RegionORM(id_region=1, nombre_region="Default Region")
    cancha = CanchaORM(id_cancha=1, nombre_cancha="Cancha Central", fk_id_region=1)
    
    db.add_all([padel, region, cancha])
    db.commit()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def context():
    """Diccionario compartido para almacenar IDs y tokens entre pasos Gherkin."""
    return {"users": {}, "teams": {}, "matches": {}}

@pytest.fixture(scope="function")
def client(db_session: Session):
    """Fixture para el TestClient de FastAPI con la BD de pruebas inyectada."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
