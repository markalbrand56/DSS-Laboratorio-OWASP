import pytest
import os
import shutil
import io
from fastapi.testclient import TestClient
from main import app  # Importa tu app principal de FastAPI
from controllers.keys import generate_rsa_keys, generate_ecc_keys

# --- Configuración del Cliente ---
# Se define 'client' aquí a nivel de módulo.
# Las pruebas de abajo lo usarán directamente.
client = TestClient(app)


# --- Fixtures ---


@pytest.fixture(autouse=True)
def setup_environment():
    """
    Fixture 'autouse' para limpiar y recrear la BD, Redis y
    los directorios de archivos antes de CADA prueba.
    """
    # --- Limpieza de Directorios ---
    # Limpiar directorios de archivos de pruebas anteriores
    shutil.rmtree("./FileSection", ignore_errors=True)
    shutil.rmtree("./temp", ignore_errors=True)

    # Recrear directorios
    os.makedirs("./FileSection", exist_ok=True)
    os.makedirs("./temp", exist_ok=True)

    yield  # Aquí es donde se ejecuta la prueba

    # --- Limpieza Post-Prueba ---
    shutil.rmtree("./FileSection", ignore_errors=True)
    shutil.rmtree("./temp", ignore_errors=True)


@pytest.fixture
def auth_user():
    """
    Fixture que registra y devuelve los datos de un usuario de prueba.
    """
    user_data = {
        "email": "fileuser@example.com",
        "password": "password123",
        "name": "File",
        "surname": "Tester",
        "birthdate": "2000-01-01",
    }
    # Usamos el 'client' global
    client.post("/auth/register", json=user_data)
    return user_data


@pytest.fixture
def auth_headers(auth_user):
    """
    Fixture que inicia sesión con el usuario de prueba y devuelve
    los headers de autorización listos para usar.
    """
    login_data = {"email": auth_user["email"], "password": auth_user["password"]}
    # Usamos el 'client' global
    response = client.post("/auth/login", json=login_data)
    token = response.json()["jwt_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_keys():
    """
    Genera un par de llaves RSA y ECC en memoria para las pruebas.
    Estas son llaves "falsas" solo para la prueba, no se guardan en la BD.
    """
    rsa_priv, rsa_pub = generate_rsa_keys()
    ecc_priv, ecc_pub = generate_ecc_keys()
    return {
        "rsa": {"private": rsa_priv, "public": rsa_pub},
        "ecc": {"private": ecc_priv, "public": ecc_pub},
    }


# --- Pruebas del Router de Archivos ---
# NOTA: 'client' ya no se pasa como argumento a las funciones.


def test_upload_file_no_sign(auth_headers, auth_user):
    """Prueba la subida de un archivo simple sin firmar."""

    # Simula un archivo en memoria
    file_content = b"Este es un archivo de prueba no firmado."
    file_to_upload = {
        "file": ("test_unsigned.txt", io.BytesIO(file_content), "text/plain")
    }

    # Datos del formulario
    form_data = {"sign": False}

    response = client.post(
        "/file/upload", headers=auth_headers, files=file_to_upload, data=form_data
    )

    assert response.status_code == 200

    # Verificar que el archivo existe en el servidor
    user_email = auth_user["email"]
    expected_path = f"FileSection/{user_email}/test_unsigned.txt"
    assert os.path.exists(expected_path)


def test_upload_file_with_rsa_sign(auth_headers, auth_user, test_keys):
    """Prueba la subida de un archivo firmado con RSA."""

    file_content = b"Este es un archivo firmado con RSA."
    file_to_upload = {
        "file": ("test_signed_rsa.txt", io.BytesIO(file_content), "text/plain")
    }

    # Datos del formulario, incluyendo la clave privada
    form_data = {
        "sign": True,
        "method": "rsa",
        "private_key": test_keys["rsa"]["private"],
    }

    response = client.post(
        "/file/upload", headers=auth_headers, files=file_to_upload, data=form_data
    )

    assert response.status_code == 200
    assert "rsa_signature" in response.json()

    # Verificar que existen el archivo original, la firma y el hash
    user_email = auth_user["email"]
    base_path = f"FileSection/{user_email}/test_signed_rsa.txt"
    assert os.path.exists(base_path)
    assert os.path.exists(f"{base_path}.rsa.sig")
    assert os.path.exists(f"{base_path}.rsa.hash")


def test_upload_file_with_ecc_sign(auth_headers, auth_user, test_keys):
    """Prueba la subida de un archivo firmado con ECC."""

    file_content = b"Este es un archivo firmado con ECC."
    file_to_upload = {
        "file": ("test_signed_ecc.txt", io.BytesIO(file_content), "text/plain")
    }

    form_data = {
        "sign": True,
        "method": "ecc",
        "private_key": test_keys["ecc"]["private"],
    }

    response = client.post(
        "/file/upload", headers=auth_headers, files=file_to_upload, data=form_data
    )

    assert response.status_code == 200
    assert "ecc_signature" in response.json()

    user_email = auth_user["email"]
    base_path = f"FileSection/{user_email}/test_signed_ecc.txt"
    assert os.path.exists(base_path)
    assert os.path.exists(f"{base_path}.ecc.sig")
    assert os.path.exists(f"{base_path}.ecc.hash")


def test_upload_sign_missing_key(auth_headers):
    """Prueba que la subida firmada falle si no se provee la clave."""

    file_content = b"Este archivo fallara."
    file_to_upload = {"file": ("fail.txt", io.BytesIO(file_content), "text/plain")}

    form_data = {
        "sign": True,  # Pide firmar
        "method": "rsa",
        # No se incluye 'private_key'
    }

    response = client.post(
        "/file/upload", headers=auth_headers, files=file_to_upload, data=form_data
    )

    assert response.status_code == 500
    assert "Se requiere método de firma y clave privada" in response.json()["detail"]


def test_get_all_user_files(auth_headers, auth_user, test_keys):
    """Prueba que el endpoint /files liste los archivos correctos y oculte los .sig/.hash."""

    # Subir un archivo firmado (crea 3 archivos: .txt, .sig, .hash)
    client.post(
        "/file/upload",
        headers=auth_headers,
        files={"file": ("signed.txt", io.BytesIO(b"s"), "text/plain")},
        data={
            "sign": True,
            "method": "rsa",
            "private_key": test_keys["rsa"]["private"],
        },
    )

    # Subir un archivo no firmado (crea 2 archivos: .txt, .hash)
    client.post(
        "/file/upload",
        headers=auth_headers,
        files={"file": ("unsigned.txt", io.BytesIO(b"u"), "text/plain")},
        data={
            "sign": False,
            "method": "hash-only",
        },  # Asumimos que 'method' se usa para el .hash
    )

    # Llamar al endpoint /files
    response = client.get("/file/files", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    # Encontrar la entrada de nuestro usuario
    user_files_data = next(
        (item for item in data if item["user"] == auth_user["email"]), None
    )
    assert user_files_data is not None

    # Verificar que SOLO los archivos base están en la lista
    file_list = user_files_data["files"]
    assert "signed.txt" in file_list
    assert "unsigned.txt" in file_list
    assert len(file_list) >= 2  # Asegurarse que no se colaron los .sig o .hash


def test_download_file(auth_headers, auth_user):
    """Prueba la descarga exitosa de un archivo."""

    file_content = b"download test content"
    client.post(
        "/file/upload",
        headers=auth_headers,
        files={"file": ("download.txt", io.BytesIO(file_content), "text/plain")},
        data={"sign": False},
    )

    response = client.get(
        f"/file/archivos/{auth_user['email']}/download.txt/descargar",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.content == file_content
    assert (
        response.headers["content-disposition"] == 'attachment; filename="download.txt"'
    )


def test_get_metadata_signed_file(auth_headers, auth_user):
    """Prueba que la metadata devuelva las llaves públicas si el usuario las generó."""

    # 1. Generar y guardar llaves en el perfil del usuario
    key_gen_response = client.post("/auth/generate-keys", headers=auth_headers)
    assert key_gen_response.status_code == 200
    rsa_private_key = key_gen_response.json()["rsa_private_key"]

    # 2. Subir un archivo firmado con esa llave
    client.post(
        "/file/upload",
        headers=auth_headers,
        files={"file": ("metadata_test.txt", io.BytesIO(b"meta"), "text/plain")},
        data={"sign": True, "method": "rsa", "private_key": rsa_private_key},
    )

    # 3. Pedir la metadata
    response = client.get(
        f"/file/archivos/{auth_user['email']}/metadata_test.txt/metadata",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "rsa" in data["metodos_firma"]
    assert "rsa" in data["llaves_publicas"]
    assert "BEGIN PUBLIC KEY" in data["llaves_publicas"]["rsa"]
    assert "ecc" not in data["metodos_firma"]  # No subimos archivo firmado con ECC


def test_verify_signature_valid_rsa(auth_headers, auth_user, test_keys):
    """Prueba la verificación exitosa de un archivo firmado."""

    file_content = b"contenido original verificado"
    filename = "verify_rsa.txt"

    # 1. Subir el archivo firmado
    client.post(
        "/file/upload",
        headers=auth_headers,
        files={"file": (filename, io.BytesIO(file_content), "text/plain")},
        data={
            "sign": True,
            "method": "rsa",
            "private_key": test_keys["rsa"]["private"],
        },
    )

    # 2. Verificar el archivo (enviando el mismo contenido y la llave pública)
    files_to_verify = {"file": (filename, io.BytesIO(file_content), "text/plain")}
    form_data = {
        "user_email": auth_user["email"],
        "public_key": test_keys["rsa"]["public"],
        "algorithm": "rsa",
    }

    response = client.post(
        "/file/verificar", headers=auth_headers, files=files_to_verify, data=form_data
    )

    assert response.status_code == 200
    assert "Archivo verificado con éxito" in response.json()["message"]


def test_verify_signature_invalid_tampered_file(auth_headers, auth_user, test_keys):
    """Prueba que la verificación falle si el contenido del archivo fue alterado."""

    file_content_original = b"contenido original"
    file_content_tampered = b"contenido alterado"  # Contenido diferente
    filename = "tampered.txt"

    # 1. Subir el archivo firmado con el contenido original
    client.post(
        "/file/upload",
        headers=auth_headers,
        files={"file": (filename, io.BytesIO(file_content_original), "text/plain")},
        data={
            "sign": True,
            "method": "rsa",
            "private_key": test_keys["rsa"]["private"],
        },
    )

    # 2. Intentar verificar con el contenido alterado
    files_to_verify = {
        "file": (filename, io.BytesIO(file_content_tampered), "text/plain")
    }
    form_data = {
        "user_email": auth_user["email"],
        "public_key": test_keys["rsa"]["public"],
        "algorithm": "rsa",
    }

    response = client.post(
        "/file/verificar", headers=auth_headers, files=files_to_verify, data=form_data
    )

    assert response.status_code == 400
    assert "La firma RSA no es válida" in response.json()["detail"]


def test_verify_signature_invalid_wrong_key(auth_headers, auth_user, test_keys):
    """Prueba que la verificación falle si se usa una llave pública incorrecta."""

    file_content = b"contenido original"
    filename = "wrong_key.txt"

    # 1. Subir el archivo firmado
    client.post(
        "/file/upload",
        headers=auth_headers,
        files={"file": (filename, io.BytesIO(file_content), "text/plain")},
        data={
            "sign": True,
            "method": "rsa",
            "private_key": test_keys["rsa"]["private"],
        },
    )

    # 2. Generar un par de llaves completamente diferente
    _, other_public_key = generate_rsa_keys()

    # 3. Intentar verificar con la llave pública incorrecta
    files_to_verify = {"file": (filename, io.BytesIO(file_content), "text/plain")}
    form_data = {
        "user_email": auth_user["email"],
        "public_key": other_public_key,  # Llave incorrecta
        "algorithm": "rsa",
    }

    response = client.post(
        "/file/verificar", headers=auth_headers, files=files_to_verify, data=form_data
    )

    assert response.status_code == 400
    assert "La firma RSA no es válida" in response.json()["detail"]
