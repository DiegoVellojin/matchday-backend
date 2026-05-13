import pytest
from pytest_bdd import scenario, given, when, then, parsers
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.modules.users.infrastructure.orm_models import UsuarioORM
from app.modules.teams.infrastructure.orm_models import EquipoORM
from app.core.security import create_access_token

@scenario('../features/teams.feature', 'Creación exitosa de un equipo')
def test_team_creation():
    pass

@scenario('../features/teams.feature', 'Unirse a un equipo y aceptar solicitud')
def test_team_join_flow():
    pass

@given(parsers.re(r'un usuario autenticado como "(?P<user_name>[^"]+)"$'))
def step_auth_user(client: TestClient, db_session: Session, context: dict, user_name: str):
    user = UsuarioORM(nombre_usuario=user_name, email_usuario=f"{user_name}@test.com", rol_usuario="Standard")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(data={"sub": str(user.id_usuario)})
    context["users"][user_name] = {"id": user.id_usuario, "token": token}

@given(parsers.re(r'un usuario autenticado como "(?P<user_name>[^"]+)" con el equipo "(?P<team_name>[^"]+)"'))
def step_auth_user_with_team(client: TestClient, db_session: Session, context: dict, user_name: str, team_name: str):
    user = UsuarioORM(nombre_usuario=user_name, email_usuario=f"{user_name}@test.com", rol_usuario="Standard")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(data={"sub": str(user.id_usuario)})
    
    team = EquipoORM(nombre_equipo=team_name, fk_id_usuario_capitan=user.id_usuario, fk_id_deporte=1)
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)
    
    context["users"][user_name] = {"id": user.id_usuario, "token": token}
    context["teams"][team_name] = team.id_equipo

@given(parsers.re(r'un usuario autenticado como "(?P<user_name>[^"]+)"'))
def step_add_auth_user(client: TestClient, db_session: Session, context: dict, user_name: str):
    # Este paso es para añadir usuarios adicionales al contexto
    if user_name not in context["users"]:
        user = UsuarioORM(nombre_usuario=user_name, email_usuario=f"{user_name}@test.com", rol_usuario="Standard")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        token = create_access_token(data={"sub": str(user.id_usuario)})
        context["users"][user_name] = {"id": user.id_usuario, "token": token}

@when(parsers.parse('intento crear un equipo llamado "{team_name}" para el deporte {sport_id:d}'))
def step_create_team(client: TestClient, context: dict, team_name: str, sport_id: int):
    # Usar el primer usuario en el contexto
    user_key = list(context["users"].keys())[0]
    token = context["users"][user_key]["token"]
    
    response = client.post(
        "/api/v1/teams/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nombre_equipo": team_name,
            "fk_id_deporte": sport_id,
            "descripcion_equipo": "Test Team"
        }
    )
    if response.status_code != 201:
        print(f"DEBUG CREATE TEAM: {response.json()}")
    assert response.status_code == 201
    context["teams"][team_name] = response.json()["id_equipo"]

@when(parsers.re(r'"(?P<user_name>[^"]+)" solicita unirse al equipo "(?P<team_name>[^"]+)"'))
def step_request_join(client: TestClient, context: dict, user_name: str, team_name: str):
    token = context["users"][user_name]["token"]
    team_id = context["teams"][team_name]
    
    response = client.post(
        f"/api/v1/teams/{team_id}/join",
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code not in [200, 201]:
        print(f"DEBUG JOIN TEAM: {response.json()}")
    assert response.status_code in [200, 201]

@when(parsers.re(r'"(?P<user_name>[^"]+)" acepta la solicitud de "(?P<player_name>[^"]+)"'))
def step_accept_request(client: TestClient, context: dict, user_name: str, player_name: str):
    token = context["users"][user_name]["token"]
    team_id = context["teams"][list(context["teams"].keys())[0]]
    player_id = context["users"][player_name]["id"]
    
    response = client.put(
        f"/api/v1/teams/{team_id}/requests/{player_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"accept": True}
    )
    if response.status_code != 200:
        print(f"DEBUG ACCEPT REQUEST: {response.json()}")
    assert response.status_code == 200

@then('el equipo es creado exitosamente')
def step_team_created(context):
    assert len(context["teams"]) > 0

@then('yo soy asignado como capitán del equipo')
def step_check_captain(client: TestClient, db_session: Session, context: dict):
    user_key = list(context["users"].keys())[0]
    user_id = context["users"][user_key]["id"]
    team_id = list(context["teams"].values())[0]
    
    team = db_session.query(EquipoORM).filter(EquipoORM.id_equipo == team_id).first()
    assert team.fk_id_usuario_capitan == user_id

@then(parsers.parse('"{user_name}" debe aparecer en la lista de miembros de "{team_name}"'))
def step_check_membership(client: TestClient, context: dict, user_name: str, team_name: str):
    # Usamos el token de cualquier usuario para ver la lista (o del capitán)
    token = list(context["users"].values())[0]["token"]
    team_id = context["teams"][team_name]
    user_id = context["users"][user_name]["id"]
    
    response = client.get(
        f"/api/v1/teams/{team_id}/members",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    members = response.json()
    assert any(m["fk_id_usuario"] == user_id for m in members)
