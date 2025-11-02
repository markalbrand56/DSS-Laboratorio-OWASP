import pytest
from fastapi.testclient import TestClient
from main import app  # Importa tu app principal de FastAPI
from database import db, User, redis_instance as r
from database.schemas import Base

# Crear el cliente de prueba
client = TestClient(app)


@pytest.fixture
def auth_headers():
    """
    Fixture que registra un usuario, inicia sesión y devuelve
    los headers de autorización listos para usar.
    """
    user_data = {
        "email": "testuser@example.com",
        "password": "password123",
        "name": "Test",
        "surname": "User",
        "birthdate": "2000-01-01"
    }

    # 1. Registrar
    client.post("/auth/register", json=user_data)

    # 2. Iniciar sesión
    login_data = {"email": user_data["email"], "password": user_data["password"]}
    response = client.post("/auth/login", json=login_data)

    assert response.status_code == 200
    token = response.json()["jwt_token"]

    # 3. Devolver headers
    return {"Authorization": f"Bearer {token}"}


# --- Pruebas de Integración de Auth ---

def test_register_success():
    """Prueba el registro exitoso de un nuevo usuario."""
    response = client.post("/auth/register", json={
        "email": "newuser@example.com",
        "password": "StrongPassword123",
        "name": "New",
        "surname": "User",
        "birthdate": "1999-05-10"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@example.com"
    assert response.json()["message"] == "User created successfully"


def test_register_user_already_exists(auth_headers):
    """Prueba que no se puede registrar un usuario con un email existente."""
    response = client.post("/auth/register", json={
        "email": "testuser@example.com",  # Este usuario ya existe por el fixture 'auth_headers'
        "password": "password123",
        "name": "Test",
        "surname": "User",
        "birthdate": "2000-01-01"
    })
    assert response.status_code == 409
    assert "User already exists" in response.json()["detail"]


def test_register_invalid_name():
    """Prueba la validación de Pydantic para caracteres HTML en el nombre."""
    response = client.post("/auth/register", json={
        "email": "baduser@example.com",
        "password": "password123",
        "name": "<script>alert(1)</script>",  # Nombre inválido
        "surname": "User",
        "birthdate": "2000-01-01"
    })
    assert response.status_code == 422  # Error de validación de FastAPI
    assert "Field cannot contain '<' or '>' characters" in str(response.json())


def test_get_me(auth_headers):
    """Prueba que el endpoint /me devuelve la info del usuario autenticado."""
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["name"] == "Test"


def test_update_me(auth_headers):
    """Prueba que se puede actualizar el perfil del usuario."""
    update_data = {
        "email": "newemail@example.com",
        "password": "NewPassword456",
        "name": "Updated",
        "surname": "Name",
        "birthdate": "2001-02-03"
    }
    response = client.put("/auth/me", headers=auth_headers, json=update_data)
    assert response.status_code == 200
    assert response.json()["message"] == "User updated successfully"

    # Verificar que los cambios se aplicaron
    # (Necesitamos un nuevo token ya que el email/payload del token anterior puede cambiar)
    new_login_resp = client.post("/auth/login", json={
        "email": "newemail@example.com",
        "password": "NewPassword456"
    })
    new_token = new_login_resp.json()["jwt_token"]
    new_headers = {"Authorization": f"Bearer {new_token}"}

    get_resp = client.get("/auth/me", headers=new_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Updated"
    assert get_resp.json()["surname"] == "Name"


def test_generate_keys(auth_headers):
    """Prueba la generación de llaves RSA y ECC."""
    response = client.post("/auth/generate-keys", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "Llaves generadas exitosamente" in data["message"]
    assert "rsa_private_key" in data
    assert "ecc_private_key" in data
    assert "BEGIN PRIVATE KEY" in data["rsa_private_key"]
    assert "BEGIN PRIVATE KEY" in data["ecc_private_key"]

    # Verificar que las llaves públicas se guardaron en la BD
    with db.read() as session:
        user = session.query(User).filter_by(email="testuser@example.com").first()
        assert user.public_key_RSA is not None
        assert user.public_key_ECC is not None
        assert "BEGIN PUBLIC KEY" in user.public_key_RSA


def test_delete_me(auth_headers):
    """Prueba que un usuario puede eliminar su propia cuenta."""
    response = client.delete("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"

    # Verificar que el usuario ya no puede iniciar sesión
    login_data = {"email": "testuser@example.com", "password": "password123"}
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401  # Credenciales inválidas (usuario no existe)

    # Verificar que el token antiguo ya no es válido
    get_resp = client.get("/auth/me", headers=auth_headers)
    assert get_resp.status_code == 401  # Usuario no encontrado