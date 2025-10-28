"""
Módulo de gestión de claves criptográficas y firmas digitales.
Proporciona funciones para generar, firmar y gestionar claves RSA y ECC.
"""
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import hashlib
from cryptography.hazmat.primitives import hashes as crypto_hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, ec
from cryptography.hazmat.primitives.asymmetric.padding import PSS, MGF1
import aiofiles
from pathlib import Path
from typing import Tuple

from backend.utils.logging_config import security_logger


async def save_hash(file_data: bytes, file_path: str, method: str = "sha256") -> str:
    """
    Calcula el hash SHA-256 del archivo y lo guarda de forma asíncrona.
    
    Args:
        file_data: Contenido del archivo en bytes
        file_path: Ruta del archivo original
        method: Método de firma utilizado (default: "sha256")
    
    Returns:
        Ruta del archivo de hash generado
    
    Raises:
        IOError: Si hay error al escribir el archivo de hash
    """
    try:
        file_hash = hashlib.sha256(file_data).hexdigest()
        hash_file_path = f"{file_path}.{method}.hash"
        
        async with aiofiles.open(hash_file_path, "w", encoding="utf-8") as f:
            await f.write(f"SHA256: {file_hash}\nFirmado con: {method}")
        
        security_logger.info(f"Hash generado exitosamente: {hash_file_path}")
        return hash_file_path
        
    except Exception as e:
        security_logger.error(f"Error al guardar hash para {file_path}: {e}")
        raise IOError(f"No se pudo guardar el hash: {e}")


async def sign_file_with_rsa(file_path: str, private_key_obj: rsa.RSAPrivateKey) -> Tuple[str, str]:
    """
    Firma un archivo usando clave privada RSA con padding PSS.
    
    Args:
        file_path: Ruta del archivo a firmar
        private_key_obj: Objeto de clave privada RSA
    
    Returns:
        Tupla con (ruta_firma, ruta_hash)
    
    Raises:
        IOError: Si hay error al leer/escribir archivos
        ValueError: Si la clave privada es inválida
    """
    try:
        # Leer archivo de forma asíncrona
        async with aiofiles.open(file_path, "rb") as f:
            file_data = await f.read()

        # Generar la firma del archivo
        signature = private_key_obj.sign(
            file_data,
            PSS(mgf=MGF1(crypto_hashes.SHA256()), salt_length=PSS.MAX_LENGTH),
            crypto_hashes.SHA256()
        )

        # Guardar la firma de forma asíncrona
        signature_path = f"{file_path}.rsa.sig"
        async with aiofiles.open(signature_path, "wb") as f:
            await f.write(signature)

        # Guardar el hash con el método 'rsa'
        hash_file_path = await save_hash(file_data, file_path, "rsa")
        
        security_logger.info(f"Archivo firmado con RSA: {file_path}")
        return signature_path, hash_file_path
        
    except Exception as e:
        security_logger.error(f"Error al firmar con RSA el archivo {file_path}: {e}")
        raise IOError(f"No se pudo firmar el archivo: {e}")


async def sign_file_with_ecc(file_path: str, private_key_obj: ec.EllipticCurvePrivateKey) -> Tuple[str, str]:
    """
    Firma un archivo usando clave privada ECC con ECDSA.
    
    Args:
        file_path: Ruta del archivo a firmar
        private_key_obj: Objeto de clave privada ECC
    
    Returns:
        Tupla con (ruta_firma, ruta_hash)
    
    Raises:
        IOError: Si hay error al leer/escribir archivos
        ValueError: Si la clave privada es inválida
    """
    try:
        # Leer archivo de forma asíncrona
        async with aiofiles.open(file_path, "rb") as f:
            file_data = await f.read()

        # Generar la firma del archivo
        signature = private_key_obj.sign(
            file_data,
            ec.ECDSA(crypto_hashes.SHA256())
        )

        # Guardar la firma de forma asíncrona
        signature_path = f"{file_path}.ecc.sig"
        async with aiofiles.open(signature_path, "wb") as f:
            await f.write(signature)

        # Guardar el hash con el método 'ecc'
        hash_file_path = await save_hash(file_data, file_path, "ecc")
        
        security_logger.info(f"Archivo firmado con ECC: {file_path}")
        return signature_path, hash_file_path
        
    except Exception as e:
        security_logger.error(f"Error al firmar con ECC el archivo {file_path}: {e}")
        raise IOError(f"No se pudo firmar el archivo: {e}")


def generate_rsa_keys() -> Tuple[str, str]:
    """
    Genera un par de claves RSA (2048 bits).
    
    Returns:
        Tupla con (clave_privada_PEM, clave_publica_PEM)
    
    Raises:
        ValueError: Si hay error en la generación de claves
    """
    try:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()

        # Serializar claves a formato PEM
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        security_logger.info("Par de claves RSA generado exitosamente")
        return private_pem.decode(), public_pem.decode()
        
    except Exception as e:
        security_logger.error(f"Error al generar claves RSA: {e}")
        raise ValueError(f"No se pudieron generar las claves RSA: {e}")


def generate_ecc_keys() -> Tuple[str, str]:
    """
    Genera un par de claves ECC usando curva secp256r1.
    
    Returns:
        Tupla con (clave_privada_PEM, clave_publica_PEM)
    
    Raises:
        ValueError: Si hay error en la generación de claves
    """
    try:
        private_key = ec.generate_private_key(ec.SECP256R1())
        public_key = private_key.public_key()

        # Serializar claves a formato PEM
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        security_logger.info("Par de claves ECC generado exitosamente")
        return private_pem.decode(), public_pem.decode()
        
    except Exception as e:
        security_logger.error(f"Error al generar claves ECC: {e}")
        raise ValueError(f"No se pudieron generar las claves ECC: {e}")


def generate_keys() -> dict:
    """
    Genera pares de claves RSA y ECC simultáneamente.
    
    Returns:
        Diccionario con claves RSA y ECC:
        {
            "rsa": {"private": str, "public": str},
            "ecc": {"private": str, "public": str}
        }
    
    Raises:
        ValueError: Si hay error en la generación de cualquiera de las claves
    """
    try:
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
    except Exception as e:
        security_logger.error(f"Error al generar conjunto de claves: {e}")
        raise ValueError(f"No se pudieron generar todas las claves: {e}")