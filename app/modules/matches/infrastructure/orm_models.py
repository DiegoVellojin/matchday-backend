from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, PrimaryKeyConstraint, Numeric, Boolean, Date
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime, date
from typing import Optional, List

class TasaCambioORM(Base):
    """Modelo ORM para el historial financiero del BCV."""
    __tablename__ = "TasaCambio"
    __table_args__ = {"schema": "bd_matchday"}

    id_tasa: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    moneda: Mapped[str] = mapped_column(String(3), nullable=False)
    monto_bs: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    fecha_referencia: Mapped[date] = mapped_column(Date, server_default=func.current_date(), nullable=False)
    fecha_captura: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    fuente: Mapped[str] = mapped_column(String(50), server_default="BCV", default="BCV", nullable=False)

class PartidaORM(Base):
    """Modelo ORM para la tabla 'Partida'."""
    __tablename__ = "Partida"
    __table_args__ = {"schema": "bd_matchday"}

    id_partida: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    fecha_inicio_estimada: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_fin_estimada: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_acordada: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    costo_total_partida: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0)
    
    # [NUEVO] Soporte Multimoneda y Capacidad
    moneda: Mapped[str] = mapped_column(String(3), default="USD", server_default="USD", nullable=False)
    cupos_totales: Mapped[int] = mapped_column(Integer, default=22, server_default="22", nullable=False)
    
    estatus_partida: Mapped[str] = mapped_column(String(20), default="publicada")
    fecha_creacion_partida: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    fk_id_usuario_org: Mapped[int] = mapped_column(Integer, ForeignKey("bd_matchday.Usuario.id_usuario"), nullable=False)
    fk_id_deporte: Mapped[int] = mapped_column(Integer, ForeignKey("bd_matchday.Deporte.id_deporte"), nullable=False)
    fk_id_cancha: Mapped[int] = mapped_column(Integer, ForeignKey("bd_matchday.Cancha.id_cancha"), nullable=False)
    fk_id_equipo_a: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("bd_matchday.Equipo.id_equipo"), nullable=True)
    fk_id_equipo_b: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("bd_matchday.Equipo.id_equipo"), nullable=True)

    # Columnas adicionales para la negociación entre capitanes
    propuesta_fecha_a: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    propuesta_costo_a: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    propuesta_moneda_a: Mapped[str] = mapped_column(String(3), default="USD", server_default="USD")
    
    propuesta_fecha_b: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    propuesta_costo_b: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    propuesta_moneda_b: Mapped[str] = mapped_column(String(3), default="USD", server_default="USD")
    
    equipo_a_listo: Mapped[bool] = mapped_column(Boolean, default=False)
    equipo_b_listo: Mapped[bool] = mapped_column(Boolean, default=False)

    # Verificación Cruzada de Resultados
    resultado_goles_a_cap_a: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resultado_goles_b_cap_a: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resultado_goles_a_cap_b: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resultado_goles_b_cap_b: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relaciones
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

    fk_id_partida: Mapped[int] = mapped_column(Integer, ForeignKey("bd_matchday.Partida.id_partida"), nullable=False)
    fk_id_usuario: Mapped[int] = mapped_column(Integer, ForeignKey("bd_matchday.Usuario.id_usuario"), nullable=False)
    estatus_pago: Mapped[str] = mapped_column(String(20), default="pendiente")
    url_recibo_pago: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    referencia_pago: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # [NUEVO] Congelamiento financiero para auditorías
    tasa_usada_bs: Mapped[Optional[float]] = mapped_column(Numeric(12, 4), nullable=True)
    monto_pagado_bs: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    
    fk_id_equipo_asignado: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("bd_matchday.Equipo.id_equipo"), nullable=True)

class ResultadoORM(Base):
    """Modelo ORM para la tabla 'Resultado'."""
    __tablename__ = "Resultado"
    __table_args__ = {"schema": "bd_matchday"}

    id_resultado: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    fk_id_partida: Mapped[int] = mapped_column(Integer, ForeignKey("bd_matchday.Partida.id_partida"), nullable=False)
    fk_id_equipo: Mapped[int] = mapped_column(Integer, ForeignKey("bd_matchday.Equipo.id_equipo"), nullable=False)
    goles_favor: Mapped[int] = mapped_column(Integer, default=0)
    goles_contra: Mapped[int] = mapped_column(Integer, default=0)
    puntos_obtenidos: Mapped[int] = mapped_column(Integer, nullable=False)
    resultado_texto: Mapped[str] = mapped_column(String(10), nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
