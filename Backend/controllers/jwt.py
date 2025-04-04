
import jwt
from jwt import DecodeError, ExpiredSignatureError,decode
from datetime import datetime, timedelta
from fastapi import HTTPException, Header, Depends
from backend.controllers.auth import get_user_by_email
from backend.database import db, User

SECRET_KEY = "clave_secreta_super_segura"

def _generate_jwt_token(user: User) -> str:
    """Genera un JWT con el ID del usuario y una expiración de 1 hora."""
    payload = {
        "user_id": user.email,
        "exp": datetime.now() + timedelta(hours=1),
        "iat": datetime.now(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_jwt(token: str) -> User:
    """Verifica el JWT y devuelve el usuario asociado."""
    try:
        payload = decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("user_id")

        if not email:
            raise HTTPException(status_code=401, detail="Token inválido: sin usuario")

        user = get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")

        return user

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except DecodeError:
        raise HTTPException(status_code=401, detail="Token inválido")


def get_current_user(authorization: str = Header(...)) -> User:
    """Obtiene el usuario actual a partir del JWT en el encabezado de autorización."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Formato de autorización inválido")
    token = authorization.split(" ")[1]
    return verify_jwt(token)