from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from backend.controllers.auth import get_current_user
from backend.controllers.FileServer import save_user_file
from backend.database import db, User

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
