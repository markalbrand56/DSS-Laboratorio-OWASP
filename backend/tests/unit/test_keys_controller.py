import os
import tempfile
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives import serialization, hashes
import asyncio

import controllers.keys as keys


def test_save_hash_creates_file_and_content():
    """Verifica que save_hash crea un archivo con el hash correcto."""
    data = b"contenido de prueba"
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "archivo.txt")
        hash_path = asyncio.run(keys.save_hash(data, file_path, "rsa"))

        assert os.path.exists(hash_path)
        with open(hash_path, "r") as f:
            contenido = f.read()
        assert "SHA256:" in contenido
        assert "Firmado con: rsa" in contenido


def test_generate_rsa_keys_valid_pem():
    """Verifica que las claves RSA se generen y sean válidas PEM."""
    priv_pem, pub_pem = keys.generate_rsa_keys()
    assert "BEGIN PRIVATE KEY" in priv_pem
    assert "BEGIN PUBLIC KEY" in pub_pem

    # Cargar para comprobar formato válido
    private = serialization.load_pem_private_key(priv_pem.encode(), password=None)
    public = serialization.load_pem_public_key(pub_pem.encode())
    assert isinstance(private, rsa.RSAPrivateKey)
    assert isinstance(public, rsa.RSAPublicKey)


def test_generate_ecc_keys_valid_pem():
    """Verifica que las claves ECC se generen y sean válidas PEM."""
    priv_pem, pub_pem = keys.generate_ecc_keys()
    assert "BEGIN PRIVATE KEY" in priv_pem
    assert "BEGIN PUBLIC KEY" in pub_pem

    private = serialization.load_pem_private_key(priv_pem.encode(), password=None)
    public = serialization.load_pem_public_key(pub_pem.encode())
    assert isinstance(private, ec.EllipticCurvePrivateKey)
    assert isinstance(public, ec.EllipticCurvePublicKey)


def test_generate_keys_combines_rsa_and_ecc(monkeypatch):
    """Verifica que generate_keys combine correctamente ambas funciones."""
    monkeypatch.setattr(keys, "generate_rsa_keys", lambda: ("priv_rsa", "pub_rsa"))
    monkeypatch.setattr(keys, "generate_ecc_keys", lambda: ("priv_ecc", "pub_ecc"))

    result = keys.generate_keys()
    assert result["rsa"]["private"] == "priv_rsa"
    assert result["rsa"]["public"] == "pub_rsa"
    assert result["ecc"]["private"] == "priv_ecc"
    assert result["ecc"]["public"] == "pub_ecc"


def test_sign_file_with_rsa_creates_signature_and_hash():
    """Verifica que sign_file_with_rsa cree archivos .sig y .hash válidos."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "archivo.txt")
        with open(file_path, "wb") as f:
            f.write(b"hola mundo")

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        sig_path, hash_path = asyncio.run(
            keys.sign_file_with_rsa(file_path, private_key)
        )

        assert os.path.exists(sig_path)
        assert os.path.exists(hash_path)

        with open(sig_path, "rb") as f:
            signature = f.read()
        assert len(signature) > 0


def test_sign_file_with_ecc_creates_signature_and_hash():
    """Verifica que sign_file_with_ecc cree archivos .sig y .hash válidos."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "archivo.txt")
        with open(file_path, "wb") as f:
            f.write(b"hola ecc")

        private_key = ec.generate_private_key(ec.SECP256R1())
        sig_path, hash_path = asyncio.run(
            keys.sign_file_with_ecc(file_path, private_key)
        )

        assert os.path.exists(sig_path)
        assert os.path.exists(hash_path)

        with open(sig_path, "rb") as f:
            signature = f.read()
        assert len(signature) > 0
