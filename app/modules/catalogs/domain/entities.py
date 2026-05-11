from typing import Optional

class Deporte:
    """
    Entidad de Dominio que representa un Deporte (Fútbol, Basket, etc).
    """
    def __init__(self, id_deporte: int, nombre_deporte: str):
        self.id_deporte = id_deporte
        self.nombre_deporte = nombre_deporte

class Region:
    def __init__(self, id_region: int, nombre_region: str, fk_id_region: Optional[int] = None):
        self.id_region = id_region
        self.nombre_region = nombre_region
        self.fk_id_region = fk_id_region

class Cancha:
    def __init__(self, id_cancha: int, nombre_cancha: str, direccion_cancha: Optional[str], fk_id_region: int, latitud_cancha: Optional[float] = None, longitud_cancha: Optional[float] = None):
        self.id_cancha = id_cancha
        self.nombre_cancha = nombre_cancha
        self.direccion_cancha = direccion_cancha
        self.fk_id_region = fk_id_region
        self.latitud_cancha = latitud_cancha
        self.longitud_cancha = longitud_cancha
