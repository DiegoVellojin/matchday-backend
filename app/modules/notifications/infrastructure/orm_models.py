from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class NotificacionORM(Base):
    __tablename__ = "Notificacion"
    __table_args__ = {"schema": "bd_matchday"}

    id_notificacion = Column(Integer, primary_key=True, index=True)
    fk_id_usuario = Column(Integer, ForeignKey("bd_matchday.Usuario.id_usuario"), nullable=False)
    mensaje = Column(String(255), nullable=False)
    leida = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, server_default=func.now())
    tipo = Column(String(50), nullable=True)
    referencia_id = Column(Integer, nullable=True)
