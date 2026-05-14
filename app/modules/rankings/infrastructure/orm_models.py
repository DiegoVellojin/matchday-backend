from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class EvaluacionORM(Base):
    """
    Modelo ORM para la tabla 'Evaluacion'.
    Registra las calificaciones que un capitán hace al equipo rival y su capitán.
    """
    __tablename__ = "Evaluacion"
    __table_args__ = {"schema": "bd_matchday"}

    id_evaluacion = Column(Integer, primary_key=True, index=True)
    fk_id_partida = Column(Integer, ForeignKey("bd_matchday.Partida.id_partida"), nullable=False)
    fk_id_evaluador = Column(Integer, ForeignKey("bd_matchday.Usuario.id_usuario"), nullable=False)
    fk_id_evaluado_equipo = Column(Integer, ForeignKey("bd_matchday.Equipo.id_equipo"), nullable=False)
    fk_id_evaluado_capitan = Column(Integer, ForeignKey("bd_matchday.Usuario.id_usuario"), nullable=False)
    puntuacion = Column(Integer, nullable=False) # 1-5 estrellas
    comentario = Column(String, nullable=True)
    fecha_evaluacion = Column(DateTime, server_default=func.now())

    # Relaciones
    partida = relationship("app.modules.matches.infrastructure.orm_models.PartidaORM")
    evaluador = relationship("app.modules.users.infrastructure.orm_models.UsuarioORM", foreign_keys=[fk_id_evaluador])
    equipo_evaluado = relationship("app.modules.teams.infrastructure.orm_models.EquipoORM", foreign_keys=[fk_id_evaluado_equipo])
    capitan_evaluado = relationship("app.modules.users.infrastructure.orm_models.UsuarioORM", foreign_keys=[fk_id_evaluado_capitan])
