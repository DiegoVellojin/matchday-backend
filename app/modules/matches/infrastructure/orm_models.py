from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, PrimaryKeyConstraint, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class PartidaORM(Base):
    """Modelo ORM para la tabla 'Partida'."""
    __tablename__ = "Partida"
    __table_args__ = {"schema": "bd_matchday"}

    id_partida = Column(Integer, primary_key=True, index=True)
    fecha_inicio_estimada = Column(DateTime, nullable=False)
    fecha_fin_estimada = Column(DateTime, nullable=False)
    fecha_acordada = Column(DateTime, nullable=True)
    costo_total_partida = Column(Numeric(10, 2), nullable=False, default=0.0)
    estatus_partida = Column(String(20), default="publicada")
    fecha_creacion_partida = Column(DateTime, server_default=func.now())
    
    fk_id_usuario_org = Column(Integer, ForeignKey("bd_matchday.Usuario.id_usuario"), nullable=False)
    fk_id_deporte = Column(Integer, ForeignKey("bd_matchday.Deporte.id_deporte"), nullable=False)
    fk_id_cancha = Column(Integer, ForeignKey("bd_matchday.Cancha.id_cancha"), nullable=False)
    fk_id_equipo_a = Column(Integer, ForeignKey("bd_matchday.Equipo.id_equipo"), nullable=True)
    fk_id_equipo_b = Column(Integer, ForeignKey("bd_matchday.Equipo.id_equipo"), nullable=True)

    # Columnas adicionales para la negociación entre capitanes
    propuesta_fecha_a = Column(DateTime, nullable=True)
    propuesta_costo_a = Column(Numeric(10, 2), nullable=True)
    propuesta_fecha_b = Column(DateTime, nullable=True)
    propuesta_costo_b = Column(Numeric(10, 2), nullable=True)
    equipo_a_listo = Column(Boolean, default=False)
    equipo_b_listo = Column(Boolean, default=False)

    # Verificación Cruzada de Resultados
    resultado_goles_a_cap_a = Column(Integer, nullable=True)
    resultado_goles_b_cap_a = Column(Integer, nullable=True)
    resultado_goles_a_cap_b = Column(Integer, nullable=True)
    resultado_goles_b_cap_b = Column(Integer, nullable=True)

    # Relaciones para evitar joins manuales
    organizador = relationship("app.modules.users.infrastructure.orm_models.UsuarioORM", foreign_keys=[fk_id_usuario_org])
    deporte = relationship("app.modules.catalogs.infrastructure.orm_models.DeporteORM", foreign_keys=[fk_id_deporte])
    cancha = relationship("app.modules.catalogs.infrastructure.orm_models.CanchaORM", foreign_keys=[fk_id_cancha])
    equipo_a = relationship("app.modules.teams.infrastructure.orm_models.EquipoORM", foreign_keys=[fk_id_equipo_a])
    equipo_b = relationship("app.modules.teams.infrastructure.orm_models.EquipoORM", foreign_keys=[fk_id_equipo_b])
    participantes = relationship("PartidaUsuarioORM", cascade="all, delete-orphan")

class PartidaUsuarioORM(Base):
    """Modelo ORM para la tabla 'Partida_Usuario'."""
    __tablename__ = "Partida_Usuario"
    __table_args__ = (
        PrimaryKeyConstraint("fk_id_partida", "fk_id_usuario"),
        {"schema": "bd_matchday"}
    )

    fk_id_partida = Column(Integer, ForeignKey("bd_matchday.Partida.id_partida"), nullable=False)
    fk_id_usuario = Column(Integer, ForeignKey("bd_matchday.Usuario.id_usuario"), nullable=False)
    estatus_pago = Column(String(20), default="pendiente")
    url_recibo_pago = Column(String(255), nullable=True)
    referencia_pago = Column(String(100), nullable=True)
    fk_id_equipo_asignado = Column(Integer, ForeignKey("bd_matchday.Equipo.id_equipo"), nullable=True)

class ResultadoORM(Base):
    """Modelo ORM para la tabla 'Resultado'."""
    __tablename__ = "Resultado"
    __table_args__ = {"schema": "bd_matchday"}

    id_resultado = Column(Integer, primary_key=True, index=True)
    fk_id_partida = Column(Integer, ForeignKey("bd_matchday.Partida.id_partida"), nullable=False)
    fk_id_equipo = Column(Integer, ForeignKey("bd_matchday.Equipo.id_equipo"), nullable=False)
    goles_favor = Column(Integer, default=0)
    goles_contra = Column(Integer, default=0)
    puntos_obtenidos = Column(Integer, nullable=False)
    resultado_texto = Column(String(10), nullable=False)
    fecha_registro = Column(DateTime, server_default=func.now())
