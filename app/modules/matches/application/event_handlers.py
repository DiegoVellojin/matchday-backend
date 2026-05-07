from app.core.events import EventDispatcher
from app.modules.matches.domain.events import TeamAssignedToMatch
from app.modules.matches.domain.interfaces import IMatchRepository
from app.core.database import SessionLocal

def handle_team_assigned(event: TeamAssignedToMatch):
    """Handler para registrar miembros del equipo cuando se asignan a un partido."""
    db = SessionLocal()
    try:
        # Aquí iría la lógica que antes estaba en el repositorio
        # Como necesitamos el repositorio para hacer el registro, 
        # lo ideal es inyectarlo o usar uno nuevo.
        from app.modules.matches.infrastructure.repositories_impl import MatchRepositoryImpl
        repo = MatchRepositoryImpl(db)
        repo._register_team_members(event.match_id, event.team_id)
        print(f"[Event] Miembros del equipo {event.team_id} registrados en partido {event.match_id}")
    finally:
        db.close()

def register_match_event_handlers():
    """Registra todos los handlers del módulo de partidos."""
    EventDispatcher.register(TeamAssignedToMatch, handle_team_assigned)
