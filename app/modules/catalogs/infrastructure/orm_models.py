from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class DeporteORM(Base):
    """
    Modelo ORM para la tabla 'Deporte'.
    """
    __tablename__ = "Deporte"
    __table_args__ = {"schema": "bd_matchday"}

    id_deporte = Column(Integer, primary_key=True, index=True)
    nombre_deporte = Column(String(50), nullable=False)

class RegionORM(Base):
    __tablename__ = "Region"
    __table_args__ = {"schema": "bd_matchday"}
    id_region = Column(Integer, primary_key=True, index=True)
    nombre_region = Column(String(100), nullable=False)
    fk_id_region = Column(Integer, nullable=True)

class CanchaORM(Base):
    __tablename__ = "Cancha"
    __table_args__ = {"schema": "bd_matchday"}
    id_cancha = Column(Integer, primary_key=True, index=True)
    nombre_cancha = Column(String(150), nullable=False)
    direccion_cancha = Column(String, nullable=True)
    latitud_cancha = Column(Float, nullable=True)
    longitud_cancha = Column(Float, nullable=True)
    fk_id_region = Column(Integer, nullable=False)
