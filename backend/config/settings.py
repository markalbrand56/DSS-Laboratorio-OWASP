"""
Configuración centralizada de la aplicación.
Utiliza variables de entorno con valores por defecto seguros.
"""
import os
from pathlib import Path
from typing import Optional

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# === SEGURIDAD ===
SECRET_KEY: str = os.getenv(
    "SECRET_KEY",
    "clave_secreta_super_segura"  # CAMBIAR EN PRODUCCIÓN
)

# Tiempo de expiración del JWT (en horas)
JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "1"))

# Algoritmo para JWT
JWT_ALGORITHM: str = "HS256"

# === REDIS (Rate Limiting) ===
REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")

# Configuración de rate limiting
MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "300"))  # 5 minutos

# === BASE DE DATOS ===
DATABASE_PATH: str = os.getenv(
    "DATABASE_PATH",
    str(BASE_DIR / "database" / "app.db")
)

# === ARCHIVOS ===
FILES_BASE_DIR: Path = Path(os.getenv("FILES_BASE_DIR", str(BASE_DIR / "FileSection")))

# === CORS ===
ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# === LOGGING ===
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR: Path = BASE_DIR / "logs"

# Crear directorios necesarios
FILES_BASE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
