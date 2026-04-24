from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class UsuarioORM(Base):
    """
    Modelo ORM de SQLAlchemy que mapea exactamente a la tabla bd_matchday."Usuario"
    """
    __tablename__ = "Usuario"
    __table_args__ = {"schema": "bd_matchday"}

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String(100), nullable=False)
    email_usuario = Column(String(100), unique=True, nullable=False)
    telefono_usuario = Column(String(20), nullable=True)
    url_foto_perfil = Column(String(255), nullable=True)
    rol_usuario = Column(String(20), nullable=False)
    reliability_score = Column(Float, default=5.00)
    fecha_creacion_usuario = Column(DateTime, server_default=func.now())
