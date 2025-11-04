import pytest
from database import redis_instance as r
from fastapi.testclient import TestClient
from main import app  # importa tu FastAPI principal

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_redis():
    """Se ejecuta antes de cada test para limpiar las llaves de login."""
    r.flushdb()
    yield
    r.flushdb()


def test_login_failed_attempts_blocked(clear_redis):
    email = "fake@example.com"
    ip = "127.0.0.1"

    # Simula 5 intentos fallidos → deben devolver 401
    for _ in range(5):
        resp = client.post("/auth/login", json={"email": email, "password": "wrong"})
        assert resp.status_code == 401

    # Sexto intento debe bloquear con 429
    resp = client.post("/auth/login", json={"email": email, "password": "wrong"})
    assert resp.status_code == 429
    assert resp.json()["detail"].startswith("Too many failed login attempts")


def test_login_resets_after_success(monkeypatch, clear_redis):
    email = "reset@example.com"

    # 3 intentos fallidos
    for _ in range(3):
        resp = client.post("/auth/login", json={"email": email, "password": "wrong"})
        assert resp.status_code == 401

    # Mock: forzar login exitoso
    monkeypatch.setattr(
        "routes.auth.login_controller", lambda e, p: (email, "fake-jwt-token")
    )

    resp = client.post(
        "/auth/login", json={"email": email, "password": "correctpassword"}
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == email
    assert "jwt_token" in resp.json()

    # Mock: volver a fallo
    monkeypatch.setattr("routes.auth.login_controller", lambda e, p: (None, None))
    resp = client.post("/auth/login", json={"email": email, "password": "wrong"})
    assert resp.status_code == 401
