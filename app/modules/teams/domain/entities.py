from datetime import datetime
from typing import Optional, List
from app.modules.catalogs.domain.entities import Deporte

class Equipo:
    """
    Entidad de Dominio que representa a un Equipo.
    """
    def __init__(
        self,
        id_equipo: Optional[int],
        nombre_equipo: str,
        fk_id_deporte: int,
        fk_id_usuario_capitan: Optional[int],
        deporte: Optional[Deporte] = None,
        url_logo_equipo: Optional[str] = None,
        puntos_acumulados: int = 0,
        descripcion_equipo: Optional[str] = None,
        esta_reclutando: bool = True,
        max_miembros: int = 11,
        fecha_creacion_equipo: Optional[datetime] = None,
        url_chat_equipo: Optional[str] = None,
        calificacion_promedio: float = 0.0,
        num_calificaciones: int = 0
    ):
        self.id_equipo = id_equipo
        self.nombre_equipo = nombre_equipo
        self.fk_id_deporte = fk_id_deporte
        self.fk_id_usuario_capitan = fk_id_usuario_capitan
        self.deporte = deporte
        self.url_logo_equipo = url_logo_equipo
        self.puntos_acumulados = puntos_acumulados
        self.descripcion_equipo = descripcion_equipo
        self.esta_reclutando = esta_reclutando
        self.max_miembros = max_miembros
        self.fecha_creacion_equipo = fecha_creacion_equipo
        self.url_chat_equipo = url_chat_equipo
        self.calificacion_promedio = calificacion_promedio
        self.num_calificaciones = num_calificaciones


class EquipoUsuario:
    """
    Entidad de Dominio que representa la relación entre un Equipo y un Usuario (Miembro).
    """
    def __init__(
        self,
        fk_id_equipo: int,
        fk_id_usuario: int,
        estatus_miembro: str = "pendiente", # 'pendiente', 'aceptado'
        rol_equipo: str = "Jugador"        # 'Capitan', 'Delegado', 'Jugador'
    ):
        self.fk_id_equipo = fk_id_equipo
        self.fk_id_usuario = fk_id_usuario
        self.estatus_miembro = estatus_miembro
        self.rol_equipo = rol_equipo
