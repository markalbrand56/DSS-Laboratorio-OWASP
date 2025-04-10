from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException
from pathlib import Path
from backend.controllers.auth import get_current_user
from backend.controllers.FileServer import save_user_file

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
    result = await save_user_file(
        file=file,
        user_email=user.email,
        sign=sign,
        method=method,
        private_key=private_key
    )
    return result


@router.get("/files")
async def get_all_user_files():
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