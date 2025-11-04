from pathlib import Path
import hashlib

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, ec
from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException
from fastapi.responses import FileResponse
import aiofiles

from controllers.FileServer import save_user_file
from controllers.auth import get_current_user
from database import db, User

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

async def verify_signature(file_path: str, public_key: str, signature: bytes, algorithm: str) -> bool:
    """
    Verifica la firma de un archivo con la clave pública proporcionada.
    Dependiendo del algoritmo de firma, puede ser RSA o ECC.
    """
    print(public_key)
    try:
        async with aiofiles.open(file_path, "rb") as f:
            file_data = await f.read()

        public_key = serialization.load_pem_public_key(public_key.encode())

        if algorithm == "rsa":
            # Verificar con RSA
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


async def _save_temp_file(file: UploadFile) -> Path:
    """Guarda el archivo temporalmente y retorna su path."""
    temp_file_path = Path("temp") / file.filename
    temp_file_path.parent.mkdir(exist_ok=True)
    
    async with aiofiles.open(temp_file_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    
    return temp_file_path


async def _verify_with_signature(temp_file_path: Path, user_dir: Path, filename: str, 
                                  public_key: str, algorithm: str) -> dict:
    """Verifica el archivo usando firma digital."""
    signature_path = user_dir / f"{filename}.{algorithm}.sig"
    
    if not signature_path.exists():
        raise HTTPException(status_code=400, detail=f"Algoritmo de firma {algorithm} no disponible.")
    
    signature_bytes = signature_path.read_bytes()
    is_valid = await verify_signature(str(temp_file_path), public_key, signature_bytes, algorithm)
    
    if is_valid:
        return {"message": f"Archivo verificado con éxito usando {algorithm.upper()}."}
    else:
        raise HTTPException(status_code=400, detail=f"La firma {algorithm.upper()} no es válida.")


async def _verify_with_hash(temp_file_path: Path, file_hash_path: Path) -> dict:
    """Verifica la integridad del archivo usando hash."""
    if not file_hash_path.exists():
        raise HTTPException(status_code=400, 
                          detail="Archivo no firmado y sin hash disponible para verificar su integridad.")
    
    async with aiofiles.open(file_hash_path, "r") as f:
        stored_hash = (await f.read()).strip()

    # Calcular el hash del archivo
    file_hash = hashlib.sha256()
    async with aiofiles.open(temp_file_path, "rb") as f:
        while chunk := await f.read(4096):
            file_hash.update(chunk)

    calculated_hash = file_hash.hexdigest()

    if stored_hash == calculated_hash:
        return {"message": "El archivo no está firmado, pero su integridad ha sido verificada con éxito."}
    else:
        raise HTTPException(status_code=400, 
                          detail="La integridad del archivo no coincide con el hash almacenado.")


@router.post("/verificar")
async def verificar_autenticidad(
        file: UploadFile = File(...),
        user_email: str = Form(...),
        public_key: str = Form(...),
        algorithm: str = Form(...)
):
    """
    Recibe un archivo y una clave pública para verificar su autenticidad.
    La clave pública debe ser del usuario que firmó el archivo.
    Si el archivo no está firmado, se verifica la integridad de los datos con la clave pública proporcionada.
    """
    # Guardar el archivo temporalmente
    temp_file_path = await _save_temp_file(file)

    # Buscar el directorio del usuario
    user_dir = BASE_DIR / user_email
    if not user_dir.exists():
        raise HTTPException(status_code=404, detail="Directorio del usuario no encontrado")

    # Buscar archivos de firma y hash
    signature_path = user_dir / f"{file.filename}.{algorithm}.sig"
    file_hash_path = user_dir / f"{file.filename}.hash"

    # Verificar si el archivo tiene una firma
    if signature_path.exists():
        return await _verify_with_signature(temp_file_path, user_dir, file.filename, public_key, algorithm)
    
    # Si no tiene firma, verificar con hash
    return await _verify_with_hash(temp_file_path, file_hash_path)