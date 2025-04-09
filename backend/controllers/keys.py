from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives import serialization


def generate_rsa_keys():
    """Genera un par de claves RSA (2048 bits) y retorna clave privada y pública."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    # Serializar claves
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem.decode(), public_pem.decode()


def generate_ecc_keys():
    """Genera un par de claves ECC (secp256r1) y retorna clave privada y pública."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    # Serializar claves
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem.decode(), public_pem.decode()

def generate_keys():
    """Genera un par de claves RSA y ECC y retorna ambas claves privadas y públicas."""
    rsa_private, rsa_public = generate_rsa_keys()
    ecc_private, ecc_public = generate_ecc_keys()

    return {
        "rsa": {
            "private": rsa_private,
            "public": rsa_public
        },
        "ecc": {
            "private": ecc_private,
            "public": ecc_public
        }
    }