from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from backend.controllers.auth import get_current_user
from backend.controllers.FileServer import save_user_file
from backend.database import db, User
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from typing import Optional

BASE_DIR = Path("FileSection")
router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    sign: bool = Form(False),
    method: str = Form(None),
    private_key: str = Form(None),
    user=Depends(get_current_user)
):

    """Sube un archivo a la carpeta del usuario.
    Si se especifica el método y la clave privada, firma el archivo.
    """
    result = await save_user_file(
        file=file,
        user_email=user.email,
        sign=sign,
        method=method,
        private_key=private_key
    )
    return result


@router.get("/files")
async def get_all_user_files(
    user=Depends(get_current_user)
):
    """
    Obtiene todos los archivos subidos por cada usuario,
    excluyendo los archivos de hash (.hash.txt) y firmas (.sig).
    Devuelve la información agrupada por usuario.
    """
    try:
        all_users_files = []

        for user_folder in BASE_DIR.iterdir():
            if user_folder.is_dir():
                user_email = user_folder.name
                user_files = []

                for file in user_folder.iterdir():
                    if (
                        file.is_file() and
                        not file.name.endswith(".hash.txt") and
                        not file.name.endswith(".sig")
                    ):
                        user_files.append(file.name)  # Solo el nombre del archivo

                all_users_files.append({
                    "user": user_email,
                    "files": user_files
                })

        return all_users_files

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener archivos: {e}")


@router.get("/archivos/{user_email}/{filename}/descargar")
async def descargar_archivo(
        user_email: str,
        filename: str,
        current_user=Depends(get_current_user)
):
    file_path = BASE_DIR / user_email / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    return FileResponse(path=str(file_path), filename=filename, media_type="application/octet-stream")


@router.get("/archivos/{user_email}/{filename}/metadata")
async def obtener_metadata(
    user_email: str,
    filename: str,
    current_user = Depends(get_current_user)
):
    file_path = BASE_DIR / user_email / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    rsa_signature = file_path.with_suffix(file_path.suffix + ".rsa.sig")
    ecc_signature = file_path.with_suffix(file_path.suffix + ".ecc.sig")

    with db.read() as session:
        user = session.query(User).filter_by(email=user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        metodo_firma = []
        public_keys = {}

        if rsa_signature.exists() and user.public_key_RSA:
            metodo_firma.append("rsa")
            public_keys["rsa"] = user.public_key_RSA

        if ecc_signature.exists() and user.public_key_ECC:
            metodo_firma.append("ecc")
            public_keys["ecc"] = user.public_key_ECC

    return {
        "metodos_firma": metodo_firma,
        "llaves_publicas": public_keys
    }

async def verify_signature(file_path: str, public_key: str, signature: bytes, algorithm: str) -> bool:
    """
    Verifica la firma de un archivo con la clave pública proporcionada.
    Dependiendo del algoritmo de firma, puede ser RSA o ECC.
    """
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()

        public_key = serialization.load_pem_public_key(public_key.encode())

        if algorithm == "rsa":
            # Verificar con RSA
            public_key.verify(
                signature,
                file_data,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
        elif algorithm == "ecc":
            # Verificar con ECC
            public_key.verify(
                signature,
                file_data,
                ec.ECDSA(hashes.SHA256())
            )
        else:
            raise ValueError("Método de firma no soportado.")

        return True
    except InvalidSignature:
        return False
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar la firma: {str(e)}")


@router.post("/verificar")
async def verificar_autenticidad(
        file: UploadFile = File(...),  # Archivo a verificar
        user_email: str = Form(...),  # Correo del propietario del archivo
        public_key: str = Form(...),  # Clave pública del propietario
        algorithm: str = Form(...)  # Algoritmo de firma ('rsa' o 'ecc')
):
    """
    Recibe un archivo y una clave pública para verificar su autenticidad.
    La clave pública debe ser del usuario que firmó el archivo.
    Si el archivo no está firmado, se verifica la integridad de los datos con la clave pública proporcionada.
    """
    # Guardar el archivo temporalmente
    temp_file_path = Path("temp") / file.filename
    with open(temp_file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Buscar el usuario en la base de datos
    with db.read() as session:
        user = session.query(User).filter_by(email=user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Verificar si el archivo está firmado
    signature_path = temp_file_path.with_suffix(temp_file_path.suffix + ".sig")

    if signature_path.exists():
        # Si la firma existe, verificarla según el algoritmo
        if algorithm == "rsa" and user.public_key_RSA:
            if verify_signature(str(temp_file_path), public_key, signature_path.read_bytes(), "rsa"):
                return {"message": "Archivo verificado con éxito usando RSA."}
            else:
                raise HTTPException(status_code=400, detail="La firma RSA no es válida.")
        elif algorithm == "ecc" and user.public_key_ECC:
            if verify_signature(str(temp_file_path), public_key, signature_path.read_bytes(), "ecc"):
                return {"message": "Archivo verificado con éxito usando ECC."}
            else:
                raise HTTPException(status_code=400, detail="La firma ECC no es válida.")
        else:
            raise HTTPException(status_code=400, detail="Algoritmo de firma no válido o no disponible.")

    # Si el archivo no está firmado, simplemente verificar la integridad con la clave pública
    else:
        # Aquí se puede hacer alguna verificación de integridad, como un hash del archivo
        return {"message": "El archivo no está firmado, pero su integridad puede verificarse."}

    raise HTTPException(status_code=400, detail="No se pudo verificar el archivo.")