import pytest
from jose import jwt
from fastapi import HTTPException

import controllers.auth as auth


# --- mocks ---
class DummyUser:
    def __init__(self, email="test@example.com", password="hash123"):
        self.email = email
        self.password = password


def test_hash_password_sha256():
    """Verifica que _hash_password produzca un hash SHA-256 consistente."""
    p1 = auth._hash_password("abc123")
    p2 = auth._hash_password("abc123")
    assert p1 == p2
    assert len(p1) == 64  # hash sha256 = 64 chars hex


def test_generate_jwt_token_contains_expected_fields():
    """Verifica que el JWT tenga campos esperados."""
    user = DummyUser()
    token = auth._generate_jwt_token(user)
    decoded = jwt.decode(token, auth.SECRET_KEY, algorithms=["HS256"])
    assert decoded["user_id"] == user.email
    assert "exp" in decoded
    assert "iat" in decoded


def test_verify_jwt_valid(monkeypatch):
    """Verifica un token JWT válido."""
    user = DummyUser()
    token = auth._generate_jwt_token(user)

    def mock_get_user_by_email(email):
        assert email == user.email
        return user

    monkeypatch.setattr(auth, "get_user_by_email", mock_get_user_by_email)
    result = auth.verify_jwt(token)
    assert result == user


def test_verify_jwt_expired(monkeypatch):
    """Simula token expirado."""
    user = DummyUser()
    payload = {
        "user_id": user.email,
        "exp": 0,  # ya expirado
        "iat": 0,
    }
    token = jwt.encode(payload, auth.SECRET_KEY, algorithm="HS256")

    with pytest.raises(HTTPException) as excinfo:
        auth.verify_jwt(token)
    assert excinfo.value.status_code == 401
    assert "expirado" in excinfo.value.detail.lower()


def test_verify_jwt_invalid(monkeypatch):
    """Simula token inválido (mal formado)."""
    with pytest.raises(HTTPException) as excinfo:
        auth.verify_jwt("token_invalido")
    assert excinfo.value.status_code == 401
    assert "inválido" in excinfo.value.detail.lower()


def test_verify_jwt_user_not_found(monkeypatch):
    """Simula token válido pero sin usuario."""
    user = DummyUser()
    token = auth._generate_jwt_token(user)

    def mock_get_user_by_email(_):
        return None

    monkeypatch.setattr(auth, "get_user_by_email", mock_get_user_by_email)

    with pytest.raises(HTTPException) as excinfo:
        auth.verify_jwt(token)
    assert excinfo.value.status_code == 401
    assert "usuario" in excinfo.value.detail.lower()


def test_get_current_user_valid(monkeypatch):
    """Verifica que extraiga el token correctamente del header."""
    user = DummyUser()
    token = auth._generate_jwt_token(user)

    def mock_verify_jwt(tok):
        assert tok == token
        return user

    monkeypatch.setattr(auth, "verify_jwt", mock_verify_jwt)
    result = auth.get_current_user(f"Bearer {token}")
    assert result == user


def test_get_current_user_invalid_format():
    """Debe lanzar error si el encabezado no comienza con Bearer."""
    with pytest.raises(HTTPException) as excinfo:
        auth.get_current_user("Token123")
    assert excinfo.value.status_code == 400


def test_login_success(monkeypatch):
    """Simula login exitoso."""
    user = DummyUser(password=auth._hash_password("pass123"))

    def mock_query(_):
        class Q:
            def filter_by(self, **kwargs):
                return self

            def first(self):
                return user

        return Q()

    class DummyDB:
        def __enter__(self):
            """Simula contexto de base de datos."""
            return self

        def __exit__(self, *a):
            """Cerrar contexto."""
            pass

        def query(self, _):
            """Simula consulta de usuario."""
            return mock_query(_)

    monkeypatch.setattr(auth.db, "write", lambda: DummyDB())

    email, token = auth.login(user.email, "pass123")
    assert email == user.email
    decoded = jwt.decode(token, auth.SECRET_KEY, algorithms=["HS256"])
    assert decoded["user_id"] == user.email


def test_login_failure(monkeypatch):
    """Simula credenciales incorrectas."""

    class DummyDB:
        def __enter__(self):
            """Simula contexto de base de datos."""
            return self

        def __exit__(self, *a):
            """Cerrar contexto."""
            pass

        def query(self, _):
            """Simula consulta de usuario que no existe."""
            class Q:
                def filter_by(self, **kwargs):
                    return self

                def first(self):
                    return None

            return Q()

    monkeypatch.setattr(auth.db, "write", lambda: DummyDB())
    email, token = auth.login("bad@example.com", "wrong")
    assert email == ""
    assert token == ""
