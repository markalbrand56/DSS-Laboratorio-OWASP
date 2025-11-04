import hashlib

from jose import jwt
from jose.exceptions import ExpiredSignatureError
import os
from fastapi import HTTPException, Header

from database import db, User
from datetime import datetime, timedelta, timezone

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")


def _generate_jwt_token(user: User) -> str:
    """Genera un JWT con el ID del usuario y una expiración de 1 hora."""
    now = datetime.now(timezone.utc)  # <-- UTC explícito
    payload = {
        "user_id": user.email,
        "exp": int((now + timedelta(hours=1)).timestamp()),
        "iat": int(now.timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_jwt(token: str) -> User:
    """Verifica el JWT y devuelve el usuario asociado."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("user_id")

        if not email:
            raise HTTPException(status_code=401, detail="Token inválido: sin usuario")

        user = get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")

        return user

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")


def get_current_user(authorization: str = Header(...)) -> User:
    """Obtiene el usuario actual a partir del JWT en el encabezado de autorización."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Formato de autorización inválido")
    token = authorization.split(" ")[1]
    return verify_jwt(token)


"""

----------------------- AUTH -----------------------

"""


def _hash_password(password: str) -> str:
    """Hashea la contraseña con SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def get_user_by_email(email: str) -> User:
    """Obtiene un usuario por su correo electrónico."""
    with db.read() as session:
        return session.query(User).filter_by(email=email).first()


def register(
        email: str,
        password: str,
        name: str = None,
        surname: str = None,
        birthdate: str = None,
) -> User:
    """Crea un nuevo usuario con la contraseña hasheada usando SHA-256."""
    hashed_password = _hash_password(password)

    with db.write() as session:
        user = User(
            email=email,
            password=hashed_password,
            name=name,
            surname=surname,
            birthdate=birthdate,
        )
        session.add(user)
        session.commit()
        return user


def login(email: str, password: str) -> tuple[str, str]:
    """Inicia sesión y devuelve email + token si las credenciales son válidas."""

    with db.write() as session:
        user = session.query(User).filter_by(email=email).first()

        if not user or user.password != _hash_password(password):
            return "", ""

        token = _generate_jwt_token(user)
        return user.email, token


def delete_user(email: str) -> bool:
    """Elimina el usuario por email."""
    with db.write() as session:
        user = session.query(User).filter_by(email=email).first()
        if not user:
            return False
        session.delete(user)
        session.commit()
        return True


def update(
        id: str = None,
        email: str = None,
        password: str = None,
        name: str = None,
        surname: str = None,
        birthdate: str = None,
) -> User:
    """
    Actualiza un usuario con la contraseña hasheada usando SHA-256.

    :param id: Email original del usuario a actualizar.
    :param email: Nuevo email del usuario (opcional).
    :param password: Nueva contraseña del usuario (opcional).
    :param name: Nuevo nombre del usuario (opcional).
    :param surname: Nuevo apellido del usuario (opcional).
    :param birthdate: Nueva fecha de nacimiento del usuario (opcional).
    :return: Usuario actualizado o None si no se encuentra.
    """
    with db.write() as session:
        user = session.query(User).filter_by(email=id).first()

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if email is not None:
            user.email = email
        if password is not None:
            hashed_password = _hash_password(password)
            user.password = hashed_password
        if name is not None:
            user.name = name
        if surname is not None:
            user.surname = surname
        if birthdate is not None:
            user.birthdate = birthdate

        return user


if __name__ == "__main__":
    # Test the functions
    try:
        register(email="test@email.com", password="password123")
    except Exception as e:
        print(f"Error creating user: {e}")

    print(login(email="test@email.com", password="password123"))
