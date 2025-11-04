import logging
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.schemas import Base

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Database:
    """Clase para la conexión a la base de datos SQLite."""

    def __init__(self, db_path: str):
        """
        Conecta a la base de datos SQLite y crea el motor.

        :param db_path: Ruta al archivo de la base de datos SQLite
        """
        self.db_path = db_path
        self.engine = None
        self.session_factory = None

        self.connect()
        self.session_factory = sessionmaker(bind=self.engine)
        self.create_tables()

    def connect(self):
        """Conecta a la base de datos SQLite y crea un motor."""
        connection_string = f"sqlite:///{self.db_path}"
        self.engine = create_engine(connection_string, echo=True)

    def create_tables(self):
        """Crea las tablas en la base de datos si no existen."""
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """
        Obtiene una sesión de la base de datos.

        :return: Sesión de la base de datos
        """
        return self.session_factory()

    @contextmanager
    def write(self):
        """
        Crea una sesión de la base de datos para realizar alguna operación de escritura (INSERT, UPDATE, DELETE) con validación de errores.

        :return: Sesión de base de datos y el código de estado
        """
        session = self.get_session()
        try:
            yield session  # Yield the session to the 'with' block
            session.commit()
        except Exception as error:
            logger.error(f"Error en la operación de escritura: {error}")
            session.rollback()
            raise  # Re-raise the exception to propagate it
        finally:
            session.close()

    @contextmanager
    def read(self):
        """
        Crea una sesión de la base de datos para realizar alguna operación de lectura (SELECT) con validación de errores.

        :return: Sesión de base de datos
        """
        session = self.get_session()
        try:
            yield session
        except Exception as error:
            logger.error(f"Error en la operación de lectura: {error}")
            session.rollback()
        finally:
            session.close()

if __name__ == "__main__":
    import os
    from database.schemas import User

    current_directory = os.path.dirname(os.path.abspath(__file__))
    db = Database(f"{current_directory}/example.db")

    with db.write() as session:
        # Create a test user
        test_user = User(email="test@example.com", password="password123")
        session.add(test_user)

    with db.read() as session:
        # Query the test user
        user = session.query(User).filter_by(email="test@example.com").first()
        print(f"User: {user.email}, Password: {user.password}")