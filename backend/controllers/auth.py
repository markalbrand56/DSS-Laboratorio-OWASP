import hashlib
from backend.database import db, User

def hash_password(password: str) -> str:
    """Hashea la contraseña con SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_email(email: str) -> User:
    """Obtiene un usuario por su correo electrónico."""
    with db.read() as session:
        return session.query(User).filter_by(email=email).first()

def create_user(email: str, password: str) -> User:
    """Crea un nuevo usuario con la contraseña hasheada usando SHA-256."""
    hashed_password = hash_password(password)
    with db.write() as session:
        user = User(email=email, password=hashed_password)
        session.add(user)
        session.commit()
        return user

def login(email: str, password: str) -> User:
    """Inicia sesión comparando el hash de la contraseña ingresada con la almacenada."""
    with db.read() as session:
        user = session.query(User).filter_by(email=email).first()
        if user and user.password == hash_password(password):
            return user
        else:
            raise Exception("Invalid credentials")


if __name__ == "__main__":
    # Test the functions
    try:
        create_user(email="test@email.com", password="password123")
    except Exception as e:
        print(f"Error creating user: {e}")

    print(login(email="test@email.com", password="password123"))
