from .database import Database
from .schemas import User
import os
import redis

current_directory = os.path.dirname(os.path.abspath(__file__))
db = Database(f"{current_directory}/database.db")


redis_instance = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=6379,
    db=0,
    decode_responses=True
)

__all__ = [
    "db",
    "User",
    "redis_instance"
]