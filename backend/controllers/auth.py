import hashlib
import jwt
from datetime import datetime, timedelta
from backend.database import db, User

SECRET_KEY = "clave_secreta_super_segura"

def _hash_password(password: str) -> str:
    """Hashea la contraseña con SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def _generate_jwt_token(user: User) -> str:
    """Genera un JWT con el ID del usuario y una expiración de 1 hora."""
    payload = {
        "user_id": user.email,
        "exp": datetime.now() + timedelta(hours=1),
        "iat": datetime.now(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def get_user_by_email(email: str) -> User:
    """Obtiene un usuario por su correo electrónico."""
    with db.read() as session:
        return session.query(User).filter_by(email=email).first()

def register(email: str, password: str) -> User:
    """Crea un nuevo usuario con la contraseña hasheada usando SHA-256."""
    hashed_password = _hash_password(password)
    with db.write() as session:
        user = User(email=email, password=hashed_password)
        session.add(user)
        session.commit()
        return user

def login(email: str, password: str) -> tuple[str, str]:
    """Inicia sesión comparando el hash de la contraseña ingresada con la almacenada."""
    with db.read() as session:
        user = session.query(User).filter_by(email=email).first()
        if user and user.password == _hash_password(password):
            return user.email, _generate_jwt_token(user)
        else:
            return "", ""


if __name__ == "__main__":
    # Test the functions
    try:
        register(email="test@email.com", password="password123")
    except Exception as e:
        print(f"Error creating user: {e}")

    print(login(email="test@email.com", password="password123"))
