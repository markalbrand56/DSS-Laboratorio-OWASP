from .database import Database
from .schemas import User
import os
import redis

from backend.config.settings import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD

current_directory = os.path.dirname(os.path.abspath(__file__))
db = Database(f"{current_directory}/database.db")

# Configurar Redis con valores de settings
redis_instance = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

# Limpiar Redis al iniciar (comentar en producción si no deseas esto)
redis_instance.flushall()

__all__ = [
    "db",
    "User",
    "redis_instance",
]