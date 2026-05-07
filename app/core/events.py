from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Callable, Dict, Type, Any

@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """Base para todos los eventos de dominio."""
    occurred_on: datetime = field(default_factory=datetime.now)

class EventDispatcher:
    """Un despachador de eventos simple (Patrón Observer/Pub-Sub)."""
    _handlers: Dict[Type[DomainEvent], List[Callable]] = {}

    @classmethod
    def register(cls, event_type: Type[DomainEvent], handler: Callable):
        if event_type not in cls._handlers:
            cls._handlers[event_type] = []
        cls._handlers[event_type].append(handler)

    @classmethod
    def dispatch(cls, event: DomainEvent):
        event_type = type(event)
        if event_type in cls._handlers:
            for handler in cls._handlers[event_type]:
                handler(event)

class AggregateRoot:
    """Mixin para entidades que pueden disparar eventos de dominio."""
    def __init__(self):
        self._domain_events: List[DomainEvent] = []

    def record_event(self, event: DomainEvent):
        self._domain_events.append(event)

    def pull_domain_events(self) -> List[DomainEvent]:
        events = self._domain_events[:]
        self._domain_events.clear()
        return events
