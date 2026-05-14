from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
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
    password_hash = Column(String(255), nullable=True)
    telefono_usuario = Column(String(20), nullable=True)
    url_foto_perfil = Column(String(255), nullable=True)
    rol_usuario = Column(String(20), nullable=False, default="Standard")
    reliability_score = Column(Float, default=5.00)
    num_calificaciones_capitan = Column(Integer, default=0)
    fecha_creacion_usuario = Column(DateTime, server_default=func.now())

    # Relaciones
    datos_bancarios = relationship("DatosBancariosORM", back_populates="usuario", uselist=False)

class UsuarioFCMORM(Base):
    """
    Modelo ORM que mapea a la tabla bd_matchday."Usuario_FCM"
    """
    __tablename__ = "Usuario_FCM"
    __table_args__ = {"schema": "bd_matchday"}

    id_token = Column(Integer, primary_key=True, index=True)
    fk_id_usuario = Column(Integer, nullable=False)
    fcm_token = Column(String, unique=True, nullable=False)
    fecha_registro = Column(DateTime, server_default=func.now())

class DatosBancariosORM(Base):
    """
    Modelo ORM que mapea a la tabla bd_matchday."Datos_Bancarios"
    """
    __tablename__ = "Datos_Bancarios"
    __table_args__ = {"schema": "bd_matchday"}

    id_datos = Column(Integer, primary_key=True, index=True)
    fk_id_usuario = Column(Integer, ForeignKey("bd_matchday.Usuario.id_usuario"), nullable=False)
    banco = Column(String(100), nullable=False)
    cedula = Column(String(50), nullable=False)
    telefono = Column(String(50), nullable=False)

    # Relaciones
    usuario = relationship("UsuarioORM", back_populates="datos_bancarios")
