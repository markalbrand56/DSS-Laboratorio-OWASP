"""
Módulo para gestión de archivos de usuarios.
Proporciona funciones asíncronas para subir, firmar y hashear archivos.
"""
import aiofiles
from pathlib import Path
from fastapi import UploadFile, HTTPException
from cryptography.hazmat.primitives import serialization
from typing import Dict, Optional

from controllers.keys import (
    sign_file_with_rsa,
    sign_file_with_ecc,
    save_hash
)
from utils.logging_config import file_logger

BASE_DIR = Path("FileSection")


async def _load_private_key(private_key_str: str):
    """
    Carga y valida una clave privada desde string PEM.
    
    Args:
        private_key_str: Clave privada en formato PEM (puede tener \\n escapados)
    
    Returns:
        Objeto de clave privada cargada
    
    Raises:
        HTTPException: Si la clave privada es inválida
    """
    try:
        # Limpiar saltos de línea escapados
        cleaned_key = private_key_str.replace("\\n", "\n").encode()
        key = serialization.load_pem_private_key(cleaned_key, password=None)
        file_logger.debug("Clave privada cargada exitosamente")
        return key
    except Exception as e:
        file_logger.error(f"Error al cargar clave privada: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Error al cargar la clave privada: {e}"
        )


async def _sign_file(
    file_path: str,
    method: str,
    private_key
) -> str:
    """
    Firma un archivo usando el método especificado.
    
    Args:
        file_path: Ruta del archivo a firmar
        method: Método de firma ('rsa' o 'ecc')
        private_key: Objeto de clave privada
    
    Returns:
        Ruta del archivo de firma generado
    
    Raises:
        HTTPException: Si el método es inválido o hay error en la firma
    """
    try:
        if method == "rsa":
            signature_path, _ = await sign_file_with_rsa(str(file_path), private_key)
            file_logger.info(f"Archivo firmado con RSA: {file_path}")
            return signature_path
        elif method == "ecc":
            signature_path, _ = await sign_file_with_ecc(str(file_path), private_key)
            file_logger.info(f"Archivo firmado con ECC: {file_path}")
            return signature_path
        else:
            raise HTTPException(
                status_code=400,
                detail="Método de firma inválido. Usa 'rsa' o 'ecc'."
            )
    except HTTPException:
        raise
    except Exception as e:
        file_logger.error(f"Error al firmar archivo {file_path}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error durante proceso de firma: {e}"
        )


async def save_user_file(
    file: UploadFile,
    user_email: str,
    sign: bool = False,
    method: Optional[str] = None,
    private_key: Optional[str] = None
) -> Dict[str, str]:
    """
    Guarda un archivo en la carpeta del usuario de forma asíncrona.
    Opcionalmente genera hash y firma el archivo.
    
    Args:
        file: Archivo subido por el usuario
        user_email: Email del usuario (usado como directorio)
        sign: Si debe firmar el archivo (default: False)
        method: Método de firma ('rsa' o 'ecc'), requerido si sign=True
        private_key: Clave privada en PEM, requerida si sign=True
    
    Returns:
        Diccionario con información del archivo guardado y procesado
    
    Raises:
        HTTPException: Si hay errores en el guardado, hash o firma
    """
    # Crear directorio del usuario si no existe
    user_dir = BASE_DIR / user_email
    user_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = user_dir / file.filename
    
    # Guardar archivo de forma asíncrona
    try:
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)
        file_logger.info(f"Archivo guardado: {file_path}")
    except Exception as e:
        file_logger.error(f"Error al guardar archivo {file.filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al guardar archivo: {e}"
        )
    
    # Leer archivo para procesar hash y firma
    try:
        async with aiofiles.open(file_path, "rb") as f:
            file_data = await f.read()
        
        # Generar hash del archivo
        hash_method = method if method else "sha256"
        hash_path = await save_hash(file_data, str(file_path), hash_method)
        
        response = {
            "message": "Archivo subido exitosamente",
            "file_path": str(file_path),
            "hash_path": hash_path
        }
        
        # Firmar archivo si se solicita
        if sign:
            if not method or not private_key:
                raise HTTPException(
                    status_code=400,
                    detail="Se requiere método de firma y clave privada si sign=True."
                )
            
            # Cargar y validar clave privada
            key_obj = await _load_private_key(private_key)
            
            # Firmar archivo
            signature_path = await _sign_file(str(file_path), method, key_obj)
            response[f"{method}_signature"] = signature_path
        
        file_logger.info(f"Archivo procesado exitosamente: {file.filename}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        file_logger.error(f"Error durante proceso de hash o firma para {file.filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error durante proceso de hash o firma: {e}"
        )
