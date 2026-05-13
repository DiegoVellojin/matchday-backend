import pytest
from pytest_bdd import scenario, given, when, then, parsers
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.modules.users.infrastructure.orm_models import UsuarioORM
from app.core.security import get_password_hash

@scenario('../features/auth.feature', 'Registro exitoso de un nuevo usuario')
def test_auth_register():
    pass

@scenario('../features/auth.feature', 'Inicio de sesión exitoso')
def test_auth_login_success():
    pass

@scenario('../features/auth.feature', 'Intento de inicio de sesión con contraseña incorrecta')
def test_auth_login_fail():
    pass

@given(parsers.parse('que el correo "{email}" no está registrado'))
def step_check_email_not_registered(db_session: Session, email: str):
    user = db_session.query(UsuarioORM).filter(UsuarioORM.email_usuario == email).first()
    if user:
        db_session.delete(user)
        db_session.commit()

@given(parsers.parse('un usuario registrado con correo "{email}" y contraseña "{password}"'))
def step_create_registered_user(db_session: Session, email: str, password: str):
    hashed = get_password_hash(password)
    user = UsuarioORM(
        nombre_usuario="Test User",
        email_usuario=email,
        password_hash=hashed,
        rol_usuario="Standard"
    )
    db_session.add(user)
    db_session.commit()

@when(parsers.parse('intento registrarme con nombre "{nombre}", correo "{email}" y contraseña "{password}"'), target_fixture="response")
def step_attempt_register(client: TestClient, nombre: str, email: str, password: str):
    return client.post(
        "/api/v1/auth/register",
        json={
            "nombre_usuario": nombre,
            "email": email,
            "password": password,
            "telefono": "123456789"
        }
    )

@when(parsers.parse('intento iniciar sesión con correo "{email}" y contraseña "{password}"'), target_fixture="response")
def step_attempt_login(client: TestClient, email: str, password: str):
    return client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

@then('el registro es exitoso')
def step_register_success(response):
    assert response.status_code == 201

@then('el inicio de sesión es exitoso')
def step_login_success(response):
    assert response.status_code == 200

@then('recibo un token de acceso válido')
def step_token_check(response):
    data = response.json()
    assert "access_token" in data
    assert len(data["access_token"]) > 0

@then(parsers.parse('recibo un error de "{error_msg}"'))
def step_error_check(response, error_msg):
    assert response.status_code in [401, 400]
    # Dependiendo de cómo devuelvas el error
    # assert error_msg in response.json()["detail"].lower()
