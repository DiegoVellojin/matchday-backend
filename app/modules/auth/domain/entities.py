from datetime import datetime
from typing import Optional

class Usuario:
    """
    Entidad de Dominio que representa a un Usuario en el sistema.
    Esta clase es pura, no tiene dependencias de frameworks ni de base de datos.
    """
    def __init__(
        self,
        id_usuario: Optional[int],
        nombre_usuario: str,
        email_usuario: str,
        password_hash: Optional[str],
        telefono_usuario: Optional[str],
        url_foto_perfil: Optional[str],
        rol_usuario: str,
        reliability_score: float,
        fecha_creacion_usuario: Optional[datetime]
    ):
        self.id_usuario = id_usuario
        self.nombre_usuario = nombre_usuario
        self.email_usuario = email_usuario
        self.password_hash = password_hash
        self.telefono_usuario = telefono_usuario
        self.url_foto_perfil = url_foto_perfil
        self.rol_usuario = rol_usuario
        self.reliability_score = reliability_score
        self.fecha_creacion_usuario = fecha_creacion_usuario
