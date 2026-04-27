class Deporte:
    """
    Entidad de Dominio que representa un Deporte (Fútbol, Basket, etc).
    """
    def __init__(self, id_deporte: int, nombre_deporte: str):
        self.id_deporte = id_deporte
        self.nombre_deporte = nombre_deporte
