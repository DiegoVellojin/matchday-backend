from sqlalchemy import Column, Integer, String
from app.core.database import Base

class DeporteORM(Base):
    """
    Modelo ORM para la tabla 'Deporte'.
    """
    __tablename__ = "Deporte"
    __table_args__ = {"schema": "bd_matchday"}

    id_deporte = Column(Integer, primary_key=True, index=True)
    nombre_deporte = Column(String(50), nullable=False)
