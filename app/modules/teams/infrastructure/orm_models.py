from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, PrimaryKeyConstraint, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class EquipoORM(Base):
    """
    Modelo ORM para la tabla 'Equipo'.
    """
    __tablename__ = "Equipo"
    __table_args__ = {"schema": "bd_matchday"}

    id_equipo = Column(Integer, primary_key=True, index=True)
    nombre_equipo = Column(String(100), nullable=False)
    url_logo_equipo = Column(String(255), nullable=True)
    puntos_acumulados = Column(Integer, default=0)
    fecha_creacion_equipo = Column(DateTime, server_default=func.now())
    fk_id_deporte = Column(Integer, ForeignKey("bd_matchday.Deporte.id_deporte"), nullable=False)
    fk_id_usuario_capitan = Column(Integer, ForeignKey("bd_matchday.Usuario.id_usuario"), nullable=True)
    descripcion_equipo = Column(String, nullable=True)
    url_chat_equipo = Column(String(255), nullable=True)
    esta_reclutando = Column(Boolean, default=True)
    max_miembros = Column(Integer, default=11)
    calificacion_promedio = Column(Float, default=0.0)
    num_calificaciones = Column(Integer, default=0)

    # Relaciones (Opcional, para facilitar consultas)
    capitan = relationship("app.modules.users.infrastructure.orm_models.UsuarioORM", foreign_keys=[fk_id_usuario_capitan], overlaps="capitan")

class EquipoUsuarioORM(Base):
    """
    Modelo ORM para la tabla asociativa 'Equipo_Usuario'.
    """
    __tablename__ = "Equipo_Usuario"
    __table_args__ = (
        PrimaryKeyConstraint("fk_id_equipo", "fk_id_usuario"),
        {"schema": "bd_matchday"}
    )

    fk_id_equipo = Column(Integer, ForeignKey("bd_matchday.Equipo.id_equipo"), nullable=False)
    fk_id_usuario = Column(Integer, ForeignKey("bd_matchday.Usuario.id_usuario"), nullable=False)
    estatus_miembro = Column(String(20), default="pendiente")
    rol_equipo = Column(String(20), default="Jugador", nullable=False)
