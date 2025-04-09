from fastapi import APIRouter, UploadFile, File, Depends
from backend.controllers.auth import get_current_user
from backend.controllers.FileServer import save_user_file

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    file_path = await save_user_file(file, user.email)
    return {"message": f"Archivo subido exitosamente", "path": file_path}
