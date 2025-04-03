from backend.database import db, User

def get_user_by_email(email: str) -> User:
    """Obtiene un usuario por su correo electrónico."""
    with db.read() as session:
        user = session.query(User).filter_by(email=email).first()
        return user

def create_user(email: str, password: str) -> User:
    """Crea un nuevo usuario."""
    with db.write() as session:
        user = User(email=email, password=password)
        session.add(user)
        session.commit()
        return user


if __name__ == "__main__":
    # Test the functions
    try:
        create_user(email="test@email.com", password="password123")
    except Exception as e:
        print(f"Error creating user: {e}")

    print(get_user_by_email("test@email.com"))
