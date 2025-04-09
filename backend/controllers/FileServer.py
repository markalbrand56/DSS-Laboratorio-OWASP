import os
from pathlib import Path
from fastapi import UploadFile, HTTPException

BASE_DIR = Path("FileSection")

async def save_user_file(file: UploadFile, user_email: str) -> str:
    """Guarda el archivo en una carpeta específica del usuario."""
    user_dir = BASE_DIR / user_email
    user_dir.mkdir(parents=True, exist_ok=True)

    file_path = user_dir / file.filename

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar archivo: {e}")

    return str(file_path)
