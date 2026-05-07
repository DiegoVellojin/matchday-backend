from dataclasses import dataclass
from app.core.events import DomainEvent

@dataclass(frozen=True, kw_only=True)
class TeamAssignedToMatch(DomainEvent):
    """Evento disparado cuando un equipo es asignado a un partido."""
    match_id: int
    team_id: int
