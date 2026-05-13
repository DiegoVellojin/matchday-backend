import pytest
from pytest_bdd import scenario, given, when, then, parsers
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.modules.users.infrastructure.orm_models import UsuarioORM
from app.modules.teams.infrastructure.orm_models import EquipoORM
from app.modules.matches.infrastructure.orm_models import PartidaORM
from app.core.security import create_access_token

@scenario('../features/gestion_partidos.feature', 'Acuerdo exitoso de términos entre capitanes')
def test_negotiation_flow():
    """Binds the Gherkin scenario to this test function."""
    pass

@given(parsers.re(r'un partido publicado con el organizador "(?P<user_name>[^"]+)"'))
def step_given_match_published(client: TestClient, db_session: Session, context: dict, user_name: str):
    # 1. Crear usuario organizador
    user = UsuarioORM(nombre_usuario=user_name, email_usuario=f"{user_name}@test.com", rol_usuario="Standard")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # 2. Crear equipo del organizador
    team = EquipoORM(nombre_equipo=f"Team {user_name}", fk_id_usuario_capitan=user.id_usuario, fk_id_deporte=1)
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)
    
    # 3. Crear partido
    match = PartidaORM(
        fk_id_usuario_org=user.id_usuario,
        fk_id_equipo_a=team.id_equipo,
        fk_id_deporte=1,
        fk_id_cancha=1,
        fecha_inicio_estimada=datetime.now() + timedelta(days=1),
        fecha_fin_estimada=datetime.now() + timedelta(days=1, hours=1),
        estatus_partida="publicada"
    )
    db_session.add(match)
    db_session.commit()
    db_session.refresh(match)
    
    # Generar token para CapitanA
    token_a = create_access_token(data={"sub": str(user.id_usuario)})
    
    context.update({
        "match_id": match.id_partida,
        "capitan_a_id": user.id_usuario,
        "team_a_id": team.id_equipo,
        "token_a": token_a
    })

@given(parsers.re(r'un equipo retador liderado por "(?P<user_name>[^"]+)"'))
def step_given_challenger_team(client: TestClient, db_session: Session, context: dict, user_name: str):
    # 1. Crear usuario retador
    user = UsuarioORM(nombre_usuario=user_name, email_usuario=f"{user_name}@test.com", rol_usuario="Standard")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # 2. Crear equipo retador
    team = EquipoORM(nombre_equipo=f"Team {user_name}", fk_id_usuario_capitan=user.id_usuario, fk_id_deporte=1)
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)
    
    # 3. Retador acepta el encuentro (pasa a negociando)
    token_b = create_access_token(data={"sub": str(user.id_usuario)})
    response = client.post(
        f"/api/v1/matches/{context['match_id']}/accept/{team.id_equipo}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    if response.status_code != 200:
        print(f"DEBUG ACCEPT: {response.json()}")
    assert response.status_code == 200
    
    context["capitan_b_id"] = user.id_usuario
    context["team_b_id"] = team.id_equipo
    context["token_b"] = token_b

@when(parsers.re(r'"(?P<user_name>[^"]+)" propone jugar el "(?P<fecha>[^"]+)" con un costo total de (?P<costo>\d+)'))
def step_when_propose_terms(client: TestClient, context: dict, user_name: str, fecha: str, costo: int):
    # Determinar qué token usar
    token = context["token_b"] # En este caso es CapitanB
    
    response = client.post(
        f"/api/v1/matches/{context['match_id']}/propose-terms",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "fecha_acordada": f"{fecha}T10:00:00",
            "costo_total": float(costo)
        }
    )
    if response.status_code != 200:
        print(f"DEBUG PROPOSE: {response.json()}")
    assert response.status_code == 200

@when(parsers.re(r'"(?P<user_name>[^"]+)" acepta la propuesta con los mismos términos'))
def step_when_accept_terms(client: TestClient, context: dict, user_name: str):
    # CapitanA acepta proponiendo lo mismo
    token = context["token_a"]
    
    response = client.post(
        f"/api/v1/matches/{context['match_id']}/propose-terms",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "fecha_acordada": "2026-06-01T10:00:00",
            "costo_total": 100.0
        }
    )
    if response.status_code != 200:
        print(f"DEBUG ACCEPT TERMS: {response.json()}")
    assert response.status_code == 200

@then(parsers.re(r'el estatus del partido debe cambiar a "(?P<status>[^"]+)"'))
def step_then_status_check(client: TestClient, context: dict, status: str):
    response = client.get(f"/api/v1/matches/{context['match_id']}")
    assert response.status_code == 200
    assert response.json()["estatus_partida"] == status

@then(parsers.re(r'el costo total en la base de datos debe ser (?P<costo>\d+)'))
def step_then_cost_check(client: TestClient, context: dict, costo: int):
    response = client.get(f"/api/v1/matches/{context['match_id']}")
    assert response.status_code == 200
    assert response.json()["costo_total_partida"] == float(costo)
