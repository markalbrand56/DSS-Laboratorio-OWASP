"""
Rutas para gestión de archivos: upload, download, metadata y verificación de firmas.
"""
from pathlib import Path
import hashlib
import aiofiles

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, ec
from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException
from fastapi.responses import FileResponse

from backend.controllers.FileServer import save_user_file
from backend.controllers.auth import get_current_user
from backend.database import db, User
from backend.utils.logging_config import file_logger

BASE_DIR = Path("FileSection")
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

router = APIRouter()


# ==================== ENDPOINTS ====================

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    sign: bool = Form(False),
    method: str = Form(None),
    private_key: str = Form(None),
    user=Depends(get_current_user)
):
    """
    Sube un archivo a la carpeta del usuario.
    Opcionalmente firma el archivo si se especifica método y clave privada.
    
    Args:
        file: Archivo a subir
        sign: Si debe firmar el archivo
        method: 'rsa' o 'ecc' (si sign=True)
        private_key: Clave privada PEM (si sign=True)
        user: Usuario autenticado
    """
    try:
        result = await save_user_file(
            file=file,
            user_email=user.email,
            sign=sign,
            method=method,
            private_key=private_key
        )
        file_logger.info(f"Archivo subido por {user.email}: {file.filename}")
        return result
    except Exception as e:
        file_logger.error(f"Error en upload por {user.email}: {e}")
        raise


@router.get("/files")
async def get_all_user_files(user=Depends(get_current_user)):
    """
    Obtiene todos los archivos subidos, excluyendo hashes y firmas.
    Devuelve la información agrupada por usuario.
    """
    try:
        all_users_files = []

        if not BASE_DIR.exists():
            return []

        for user_folder in BASE_DIR.iterdir():
            if not user_folder.is_dir():
                continue
                
            user_email = user_folder.name
            user_files = []

            for file in user_folder.iterdir():
                # Excluir archivos de hash y firmas
                if file.is_file() and not _is_metadata_file(file.name):
                    user_files.append(file.name)

            all_users_files.append({
                "user": user_email,
                "files": user_files
            })

        return all_users_files

    except Exception as e:
        file_logger.error(f"Error al obtener archivos: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener archivos: {e}")


@router.get("/archivos/{user_email}/{filename}/descargar")
async def descargar_archivo(
    user_email: str,
    filename: str,
    current_user=Depends(get_current_user)
):
    """Descarga un archivo específico del usuario."""
    file_path = BASE_DIR / user_email / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/octet-stream"
    )


@router.get("/archivos/{user_email}/{filename}/metadata")
async def obtener_metadata(
    user_email: str,
    filename: str,
    current_user=Depends(get_current_user)
):
    """Obtiene metadata de firma de un archivo (métodos disponibles y claves públicas)."""
    file_path = BASE_DIR / user_email / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    rsa_signature = file_path.with_suffix(file_path.suffix + ".rsa.sig")
    ecc_signature = file_path.with_suffix(file_path.suffix + ".ecc.sig")

    metodo_firma = []
    public_keys = {}

    with db.read() as session:
        user = session.query(User).filter_by(email=user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

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


@router.post("/verificar")
async def verificar_autenticidad(
    file: UploadFile = File(...),
    user_email: str = Form(...),
    public_key: str = Form(...),
    algorithm: str = Form(...)
):
    """
    Verifica la autenticidad de un archivo mediante firma digital o hash.
    
    Args:
        file: Archivo a verificar
        user_email: Email del propietario del archivo original
        public_key: Clave pública para verificación
        algorithm: Algoritmo de firma ('rsa' o 'ecc')
    
    Returns:
        Mensaje de éxito si el archivo es válido
    
    Raises:
        HTTPException: Si la verificación falla
    """
    # Validar algoritmo
    if algorithm not in ["rsa", "ecc"]:
        raise HTTPException(
            status_code=400,
            detail="Algoritmo inválido. Usa 'rsa' o 'ecc'."
        )
    
    # Guardar archivo temporal
    temp_file_path = await _save_temp_file(file)
    file_logger.info(f"Verificando archivo {file.filename} para usuario {user_email}")
    
    try:
        # Verificar que existe el directorio del usuario
        user_dir = BASE_DIR / user_email
        if not user_dir.exists():
            raise HTTPException(
                status_code=404,
                detail="Directorio del usuario no encontrado"
            )
        
        # Intentar verificar con firma
        signature_verified = await _try_verify_signature(
            temp_file_path,
            user_dir,
            file.filename,
            public_key,
            algorithm
        )
        
        if signature_verified:
            return signature_verified
        
        # Si no hay firma, verificar hash
        hash_verified = await _try_verify_hash(
            temp_file_path,
            user_dir,
            file.filename,
            algorithm
        )
        
        if hash_verified:
            return hash_verified
        
        # No hay firma ni hash
        raise HTTPException(
            status_code=400,
            detail="Archivo no firmado y sin hash disponible para verificar su integridad."
        )
    
    finally:
        # Limpiar archivo temporal
        if temp_file_path.exists():
            temp_file_path.unlink()
            file_logger.debug(f"Archivo temporal eliminado: {temp_file_path}")


# ==================== FUNCIONES HELPER ====================

def _is_metadata_file(filename: str) -> bool:
    """Verifica si un archivo es metadata (hash o firma)."""
    return filename.endswith(".hash") or filename.endswith(".sig")


async def _save_temp_file(file: UploadFile) -> Path:
    """
    Guarda un archivo subido en directorio temporal.
    
    Args:
        file: Archivo subido
    
    Returns:
        Path del archivo temporal
    """
    temp_file_path = TEMP_DIR / file.filename
    
    async with aiofiles.open(temp_file_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    
    return temp_file_path


async def _calculate_file_hash(file_path: Path) -> str:
    """
    Calcula el hash SHA-256 de un archivo de forma asíncrona.
    
    Args:
        file_path: Ruta del archivo
    
    Returns:
        Hash hexadecimal del archivo
    """
    file_hash = hashlib.sha256()
    
    async with aiofiles.open(file_path, "rb") as f:
        while chunk := await f.read(4096):
            file_hash.update(chunk)
    
    return file_hash.hexdigest()


async def _verify_signature_async(
    file_path: str,
    public_key_str: str,
    signature: bytes,
    algorithm: str
) -> bool:
    """
    Verifica la firma de un archivo de forma asíncrona.
    
    Args:
        file_path: Ruta del archivo a verificar
        public_key_str: Clave pública en formato PEM
        signature: Bytes de la firma
        algorithm: 'rsa' o 'ecc'
    
    Returns:
        True si la firma es válida, False en caso contrario
    
    Raises:
        HTTPException: Si hay error en la verificación
    """
    try:
        # Leer archivo de forma asíncrona
        async with aiofiles.open(file_path, "rb") as f:
            file_data = await f.read()

        # Cargar clave pública
        public_key = serialization.load_pem_public_key(public_key_str.encode())

        # Verificar según algoritmo
        if algorithm == "rsa":
            public_key.verify(
                signature,
                file_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        elif algorithm == "ecc":
            public_key.verify(
                signature,
                file_data,
                ec.ECDSA(hashes.SHA256())
            )
        else:
            raise ValueError(f"Algoritmo no soportado: {algorithm}")

        file_logger.info(f"Firma {algorithm} verificada exitosamente para {file_path}")
        return True
        
    except InvalidSignature:
        file_logger.warning(f"Firma {algorithm} inválida para {file_path}")
        return False
    except Exception as e:
        file_logger.error(f"Error al verificar firma {algorithm}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al verificar la firma: {str(e)}"
        )


async def _try_verify_signature(
    temp_file_path: Path,
    user_dir: Path,
    filename: str,
    public_key: str,
    algorithm: str
):
    """Intenta verificar la firma del archivo."""
    sig_path = user_dir / f"{filename}.{algorithm}.sig"
    
    if not sig_path.exists():
        return None
    
    signature = sig_path.read_bytes()
    is_valid = await _verify_signature_async(
        str(temp_file_path),
        public_key,
        signature,
        algorithm
    )
    
    if is_valid:
        return {"message": f"Archivo verificado con éxito usando {algorithm.upper()}."}
    else:
        raise HTTPException(
            status_code=400,
            detail=f"La firma {algorithm.upper()} no es válida."
        )


async def _try_verify_hash(
    temp_file_path: Path,
    user_dir: Path,
    filename: str,
    algorithm: str
):
    """Intenta verificar el hash del archivo."""
    # Buscar archivo de hash
    hash_path = user_dir / f"{filename}.{algorithm}.hash"
    if not hash_path.exists():
        hash_path = user_dir / f"{filename}.sha256.hash"
    
    if not hash_path.exists():
        return None
    
    # Leer hash almacenado
    async with aiofiles.open(hash_path, "r") as f:
        content = await f.read()
        # Extraer solo el hash (formato: "SHA256: <hash>\nFirmado con: ...")
        stored_hash = content.split("\n")[0].replace("SHA256: ", "").strip()
    
    # Calcular hash del archivo temporal
    calculated_hash = await _calculate_file_hash(temp_file_path)
    
    # Verificar integridad
    if stored_hash == calculated_hash:
        return {
            "message": "El archivo no está firmado, pero su integridad ha sido verificada con éxito."
        }
    else:
        raise HTTPException(
            status_code=400,
            detail="La integridad del archivo no coincide con el hash almacenado."
        )
