import pytest
import redis
from fastapi.testclient import TestClient
from main import app  # importa tu FastAPI principal

client = TestClient(app)

# Config redis de prueba (asegúrate que sea un db distinto al de prod)
r = redis.Redis(host="localhost", port=6379, db=1, decode_responses=True)


@pytest.fixture(autouse=True)
def clear_redis():
    """Se ejecuta antes de cada test para limpiar las llaves de login."""
    r.flushdb()
    yield
    r.flushdb()


def test_login_failed_attempts_blocked():
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


def test_login_resets_after_success(monkeypatch):
    email = "reset@example.com"
    ip = "127.0.0.1"

    # Simula intentos fallidos
    for _ in range(3):
        resp = client.post("/auth/login", json={"email": email, "password": "wrong"})
        assert resp.status_code == 401

    # Mock de login_controller para forzar un login exitoso
    from controllers import auth
    monkeypatch.setattr(auth, "login", lambda e, p: (email, "fake-jwt-token"))

    # Login exitoso
    resp = client.post("/auth/login", json={"email": email, "password": "correctpassword"})
    assert resp.status_code == 200
    assert resp.json()["email"] == email
    assert "jwt_token" in resp.json()

    # Debe resetear los intentos → otro intento fallido vuelve a 401 (no 429)
    monkeypatch.setattr(auth, "login", lambda e, p: (None, None))
    resp = client.post("/auth/login", json={"email": email, "password": "wrong"})
    assert resp.status_code == 401
