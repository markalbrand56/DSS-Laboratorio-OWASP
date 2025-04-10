import os
from pathlib import Path
from fastapi import UploadFile, HTTPException
from cryptography.hazmat.primitives import serialization
from backend.controllers.keys import (
    sign_file_with_rsa,
    sign_file_with_ecc,
    save_hash
)

BASE_DIR = Path("FileSection")


async def save_user_file(
        file: UploadFile,
        user_email: str,
        sign: bool = False,
        method: str = None,
        private_key: str = None
) -> dict:
    """
    Guarda el archivo en una carpeta del usuario. Opcionalmente:
    - Genera el hash (siempre)
    - Firma el archivo (si sign=True y se provee clave y método)
    """
    user_dir = BASE_DIR / user_email
    user_dir.mkdir(parents=True, exist_ok=True)

    file_path = user_dir / file.filename

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar archivo: {e}")

    try:
        with open(file_path, "rb") as f:
            file_data = f.read()

        #Generar el hash del archivo
        hash_path = save_hash(file_data, str(file_path), method) if method else save_hash(file_data, str(file_path))

        response = {
            "message": "Archivo subido exitosamente",
            "file_path": str(file_path),
            "hash_path": hash_path
        }

        if sign:
            if not method or not private_key:
                raise HTTPException(status_code=400, detail="Se requiere método de firma y clave privada si sign=True.")
            print("private_key\n", private_key)
            # 🔧 Limpiar y cargar la clave privada
            try:
                cleaned_key = private_key.replace("\\n", "\n").encode()
                key = serialization.load_pem_private_key(cleaned_key, password=None)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error al cargar la clave privada: {e}")

            if method == "rsa":
                signature_path, _ = sign_file_with_rsa(str(file_path), key)
                response["rsa_signature"] = signature_path
            elif method == "ecc":
                signature_path, _ = sign_file_with_ecc(str(file_path), key)
                response["ecc_signature"] = signature_path
            else:
                raise HTTPException(status_code=400, detail="Método de firma inválido. Usa 'rsa' o 'ecc'.")

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante proceso de hash o firma: {e}")
