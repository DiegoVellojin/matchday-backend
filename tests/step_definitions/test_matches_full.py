import pytest
from pytest_bdd import scenario, given, when, then, parsers
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.modules.users.infrastructure.orm_models import UsuarioORM
from app.modules.teams.infrastructure.orm_models import EquipoORM
from app.modules.matches.infrastructure.orm_models import PartidaORM
from app.core.security import create_access_token

@scenario('../features/matches_full.feature', 'Publicación de un nuevo partido')
def test_match_publication():
    pass

@scenario('../features/matches_full.feature', 'Unirse individualmente a un partido')
def test_match_join_individual():
    pass

@scenario('../features/matches_full.feature', 'Registro y confirmación de resultados')
def test_match_results_flow():
    pass

@given(parsers.re(r'un usuario autenticado como "(?P<user_name>[^"]+)"$'))
def step_auth_user(client: TestClient, db_session: Session, context: dict, user_name: str):
    user = UsuarioORM(nombre_usuario=user_name, email_usuario=f"{user_name}@test.com", rol_usuario="Standard")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(data={"sub": str(user.id_usuario)})
    context["users"][user_name] = {"id": user.id_usuario, "token": token}

@given(parsers.parse('un partido publicado por "{user_name}"'))
def step_match_published(client: TestClient, db_session: Session, context: dict, user_name: str):
    user = UsuarioORM(nombre_usuario=user_name, email_usuario=f"{user_name}@test.com", rol_usuario="Standard")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(data={"sub": str(user.id_usuario)})
    
    match = PartidaORM(
        fk_id_usuario_org=user.id_usuario,
        fk_id_deporte=1,
        fk_id_cancha=1,
        fecha_inicio_estimada=datetime.now() + timedelta(days=1),
        fecha_fin_estimada=datetime.now() + timedelta(days=1, hours=1),
        estatus_partida="publicada"
    )
    db_session.add(match)
    db_session.commit()
    db_session.refresh(match)
    
    context["users"][user_name] = {"id": user.id_usuario, "token": token}
    context["matches"]["default"] = match.id_partida

@given(parsers.parse('un partido en estado "confirmada" entre "{team_a}" y "{team_b}"'))
def step_match_confirmed(client: TestClient, db_session: Session, context: dict, team_a: str, team_b: str):
    # Crear capitanes
    user_a = UsuarioORM(nombre_usuario="CapA", email_usuario="capa@test.com")
    user_b = UsuarioORM(nombre_usuario="CapB", email_usuario="capb@test.com")
    db_session.add_all([user_a, user_b])
    db_session.commit()
    db_session.refresh(user_a)
    db_session.refresh(user_b)
    
    # Crear equipos
    t_a = EquipoORM(nombre_equipo=team_a, fk_id_usuario_capitan=user_a.id_usuario, fk_id_deporte=1)
    t_b = EquipoORM(nombre_equipo=team_b, fk_id_usuario_capitan=user_b.id_usuario, fk_id_deporte=1)
    db_session.add_all([t_a, t_b])
    db_session.commit()
    db_session.refresh(t_a)
    db_session.refresh(t_b)
    
    # Crear partido confirmado
    match = PartidaORM(
        fk_id_usuario_org=user_a.id_usuario,
        fk_id_equipo_a=t_a.id_equipo,
        fk_id_equipo_b=t_b.id_equipo,
        fk_id_deporte=1,
        fk_id_cancha=1,
        fecha_inicio_estimada=datetime.now() - timedelta(hours=2),
        fecha_fin_estimada=datetime.now() - timedelta(hours=1),
        estatus_partida="confirmada"
    )
    db_session.add(match)
    db_session.commit()
    db_session.refresh(match)
    
    context["users"]["CapA"] = {"id": user_a.id_usuario, "token": create_access_token(data={"sub": str(user_a.id_usuario)})}
    context["users"]["CapB"] = {"id": user_b.id_usuario, "token": create_access_token(data={"sub": str(user_b.id_usuario)})}
    context["matches"]["default"] = match.id_partida

@when(parsers.re(r'intento publicar un partido para el deporte (?P<sport_id>\d+) en la cancha (?P<cancha_id>\d+)'))
def step_publish_match(client: TestClient, context: dict, sport_id: int, cancha_id: int):
    user_key = list(context["users"].keys())[0]
    token = context["users"][user_key]["token"]
    
    response = client.post(
        "/api/v1/matches/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "fk_id_deporte": int(sport_id),
            "fk_id_cancha": int(cancha_id),
            "fecha_inicio_estimada": (datetime.now() + timedelta(days=1)).isoformat(),
            "fecha_fin_estimada": (datetime.now() + timedelta(days=1, hours=1)).isoformat()
        }
    )
    if response.status_code != 201:
        print(f"DEBUG PUBLISH: {response.json()}")
    assert response.status_code == 201
    context["matches"]["default"] = response.json()["id"]

@when(parsers.re(r'"(?P<user_name>[^"]+)" intenta unirse al partido'))
def step_join_match(client: TestClient, context: dict, user_name: str):
    token = context["users"][user_name]["token"]
    match_id = context["matches"]["default"]
    
    response = client.post(
        f"/api/v1/matches/{match_id}/join",
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code != 200:
        print(f"DEBUG JOIN: {response.json()}")
    assert response.status_code == 200

@when(parsers.re(r'el capitán de "(?P<team_name>[^"]+)" registra un resultado de (?P<goles_a>\d+)-(?P<goles_b>\d+)'))
def step_register_result(client: TestClient, context: dict, team_name: str, goles_a: int, goles_b: int):
    # Simplificamos: CapA es capitán de EquipoA
    user_key = "CapA" if "A" in team_name else "CapB"
    token = context["users"][user_key]["token"]
    match_id = context["matches"]["default"]
    
    response = client.post(
        f"/api/v1/matches/{match_id}/results",
        headers={"Authorization": f"Bearer {token}"},
        json={"goles_a": int(goles_a), "goles_b": int(goles_b)}
    )
    if response.status_code != 201:
        print(f"DEBUG RESULT: {response.json()}")
    assert response.status_code == 201

@then(parsers.re(r'el partido aparece en el feed como "(?P<status>[^"]+)"'))
def step_check_feed_status(client: TestClient, context: dict, status: str):
    match_id = context["matches"]["default"]
    response = client.get(f"/api/v1/matches/{match_id}")
    assert response.json()["estatus_partida"] == status

@then(parsers.re(r'"(?P<user_name>[^"]+)" debe estar en la lista de jugadores del partido'))
def step_check_players(client: TestClient, context: dict, user_name: str):
    match_id = context["matches"]["default"]
    user_id = context["users"][user_name]["id"]
    
    response = client.get(f"/api/v1/matches/{match_id}/players")
    players = response.json()
    assert any(p["id_usuario"] == user_id for p in players)

@then(parsers.re(r'el partido debe cambiar a estado "(?P<status>[^"]+)"'))
def step_check_final_status(client: TestClient, context: dict, status: str):
    match_id = context["matches"]["default"]
    response = client.get(f"/api/v1/matches/{match_id}")
    assert response.json()["estatus_partida"] == status

@then('el ranking de los equipos debe actualizarse')
def step_check_ranking(client: TestClient):
    response = client.get("/api/v1/rankings/team-leaderboard")
    assert response.status_code == 200
    leaderboard = response.json()
    if len(leaderboard) < 2:
        print(f"DEBUG RANKING: {leaderboard}")
    assert len(leaderboard) >= 2
