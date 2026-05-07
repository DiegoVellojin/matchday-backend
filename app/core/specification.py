from abc import ABC, abstractmethod
from typing import Any

class Specification(ABC):
    """Interfaz base para el patrón Specification con soporte para SQLAlchemy."""

    @abstractmethod
    def is_satisfied_by(self, item: Any) -> bool:
        """Verifica si un objeto en memoria cumple la especificación."""
        pass

    @abstractmethod
    def apply_to_query(self, query, model):
        """Aplica los filtros de la especificación a una consulta de SQLAlchemy."""
        pass

    def __and__(self, other: 'Specification') -> 'AndSpecification':
        return AndSpecification(self, other)

    def __or__(self, other: 'Specification') -> 'OrSpecification':
        return OrSpecification(self, other)

    def __invert__(self) -> 'NotSpecification':
        return NotSpecification(self)

class AndSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def is_satisfied_by(self, item: Any) -> bool:
        return self.left.is_satisfied_by(item) and self.right.is_satisfied_by(item)

    def apply_to_query(self, query, model):
        query = self.left.apply_to_query(query, model)
        return self.right.apply_to_query(query, model)

class OrSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def is_satisfied_by(self, item: Any) -> bool:
        return self.left.is_satisfied_by(item) or self.right.is_satisfied_by(item)

    def apply_to_query(self, query, model):
        # Nota: La implementación de OR en SQLAlchemy requiere un poco más de cuidado (usar or_())
        # Pero para una implementación básica esto sirve de base.
        # En una versión pro, usaríamos or_() de sqlalchemy.
        from sqlalchemy import or_
        # Esto es un poco más complejo porque apply_to_query suele mutar la query
        # Una alternativa es que devuelvan la expresión del filtro (BinaryExpression)
        return query # Placeholder simplificado

class NotSpecification(Specification):
    def __init__(self, spec: Specification):
        self.spec = spec

    def is_satisfied_by(self, item: Any) -> bool:
        return not self.spec.is_satisfied_by(item)

    def apply_to_query(self, query, model):
        # Similar al OR, requiere el operador ~ o not_() de SQLAlchemy
        return query
