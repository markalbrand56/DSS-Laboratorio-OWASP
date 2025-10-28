"""
Controlador de autenticación y gestión de usuarios.
Proporciona funciones para registro, login, JWT y manejo de usuarios.
"""
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional

import jwt
from jwt.exceptions import ExpiredSignatureError, DecodeError
from fastapi import HTTPException, Header

from database import db, User
from controllers.keys import generate_rsa_keys, generate_ecc_keys
from config.settings import SECRET_KEY, JWT_EXPIRATION_HOURS, JWT_ALGORITHM
from utils.logging_config import auth_logger


# ==================== JWT ====================

def _generate_jwt_token(user: User) -> str:
    """
    Genera un JWT con el ID del usuario y una expiración configurable.
    
    Args:
        user: Usuario para el cual generar el token
    
    Returns:
        Token JWT como string
    """
    now = datetime.now(timezone.utc)
    payload = {
        "user_id": user.email,
        "exp": int((now + timedelta(hours=JWT_EXPIRATION_HOURS)).timestamp()),
        "iat": int(now.timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_jwt(token: str) -> User:
    """
    Verifica el JWT y devuelve el usuario asociado.
    
    Args:
        token: Token JWT a verificar
    
    Returns:
        Usuario asociado al token
    
    Raises:
        HTTPException: Si el token es inválido o expirado
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email = payload.get("user_id")

        if not email:
            auth_logger.warning("Token sin usuario")
            raise HTTPException(status_code=401, detail="Token inválido: sin usuario")

        user = get_user_by_email(email)
        if not user:
            auth_logger.warning(f"Usuario no encontrado para email: {email}")
            raise HTTPException(status_code=401, detail="Usuario no encontrado")

        auth_logger.debug(f"Token verificado para usuario: {email}")
        return user

    except ExpiredSignatureError:
        auth_logger.warning("Token expirado")
        raise HTTPException(status_code=401, detail="Token expirado")
    except DecodeError as e:
        auth_logger.error(f"Error al decodificar token: {e}")
        raise HTTPException(status_code=401, detail="Token inválido")


def get_current_user(authorization: str = Header(...)) -> User:
    """
    Obtiene el usuario actual a partir del JWT en el encabezado de autorización.
    
    Args:
        authorization: Header de autorización con formato "Bearer <token>"
    
    Returns:
        Usuario autenticado
    
    Raises:
        HTTPException: Si el formato es inválido o el token no es válido
    """
    if not authorization.startswith("Bearer "):
        auth_logger.warning("Formato de autorización inválido")
        raise HTTPException(status_code=400, detail="Formato de autorización inválido")
    
    token = authorization.split(" ")[1]
    return verify_jwt(token)


# ==================== AUTENTICACIÓN ====================

def _hash_password(password: str) -> str:
    """
    Hashea la contraseña con SHA-256.
    
    NOTA: Para producción, considerar migrar a bcrypt o argon2.
    
    Args:
        password: Contraseña en texto plano
    
    Returns:
        Hash de la contraseña
    """
    return hashlib.sha256(password.encode()).hexdigest()


def get_user_by_email(email: str) -> Optional[User]:
    """
    Obtiene un usuario por su correo electrónico.
    
    Args:
        email: Email del usuario a buscar
    
    Returns:
        Usuario si existe, None en caso contrario
    """
    try:
        with db.read() as session:
            user = session.query(User).filter_by(email=email).first()
            if user:
                auth_logger.debug(f"Usuario encontrado: {email}")
            return user
    except Exception as e:
        auth_logger.error(f"Error al buscar usuario {email}: {e}")
        return None


def register(
    email: str,
    password: str,
    name: Optional[str] = None,
    surname: Optional[str] = None,
    birthdate: Optional[str] = None,
) -> User:
    """
    Crea un nuevo usuario con la contraseña hasheada.
    
    Args:
        email: Email del usuario
        password: Contraseña en texto plano
        name: Nombre del usuario (opcional)
        surname: Apellido del usuario (opcional)
        birthdate: Fecha de nacimiento (opcional)
    
    Returns:
        Usuario creado
    
    Raises:
        Exception: Si hay error en la creación
    """
    try:
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
            auth_logger.info(f"Usuario registrado exitosamente: {email}")
            return user
    except Exception as e:
        auth_logger.error(f"Error al registrar usuario {email}: {e}")
        raise


def login(email: str, password: str) -> Tuple[str, str]:
    """
    Inicia sesión y devuelve email + token si las credenciales son válidas.
    
    Args:
        email: Email del usuario
        password: Contraseña en texto plano
    
    Returns:
        Tupla (email, token) si es exitoso, ("", "") si falla
    """
    try:
        with db.write() as session:
            user = session.query(User).filter_by(email=email).first()

            if not user or user.password != _hash_password(password):
                auth_logger.warning(f"Intento de login fallido para: {email}")
                return "", ""

            token = _generate_jwt_token(user)
            auth_logger.info(f"Login exitoso para usuario: {email}")
            return user.email, token
    except Exception as e:
        auth_logger.error(f"Error en login para {email}: {e}")
        return "", ""


def delete_user(email: str) -> bool:
    """
    Elimina el usuario por email.
    
    Args:
        email: Email del usuario a eliminar
    
    Returns:
        True si se eliminó, False si no se encontró
    """
    try:
        with db.write() as session:
            user = session.query(User).filter_by(email=email).first()
            if not user:
                auth_logger.warning(f"Usuario no encontrado para eliminar: {email}")
                return False
            session.delete(user)
            session.commit()
            auth_logger.info(f"Usuario eliminado: {email}")
            return True
    except Exception as e:
        auth_logger.error(f"Error al eliminar usuario {email}: {e}")
        raise


def update(
    id: str,
    email: Optional[str] = None,
    password: Optional[str] = None,
    name: Optional[str] = None,
    surname: Optional[str] = None,
    birthdate: Optional[str] = None,
) -> User:
    """
    Actualiza un usuario existente.
    
    Args:
        id: Email original del usuario a actualizar
        email: Nuevo email (opcional)
        password: Nueva contraseña (opcional)
        name: Nuevo nombre (opcional)
        surname: Nuevo apellido (opcional)
        birthdate: Nueva fecha de nacimiento (opcional)
    
    Returns:
        Usuario actualizado
    
    Raises:
        Exception: Si el usuario no existe o hay error
    """
    try:
        with db.write() as session:
            user = session.query(User).filter_by(email=id).first()

            if not user:
                auth_logger.error(f"Usuario no encontrado para actualizar: {id}")
                raise Exception("Usuario no encontrado")

            if email is not None:
                user.email = email
            if password is not None:
                user.password = _hash_password(password)
            if name is not None:
                user.name = name
            if surname is not None:
                user.surname = surname
            if birthdate is not None:
                user.birthdate = birthdate

            auth_logger.info(f"Usuario actualizado: {id}")
            return user
    except Exception as e:
        auth_logger.error(f"Error al actualizar usuario {id}: {e}")
        raise


# ==================== TESTING ====================

if __name__ == "__main__":
    # Test the functions
    try:
        register(email="test@email.com", password="password123")
        auth_logger.info("Test: Usuario creado")
    except Exception as e:
        auth_logger.error(f"Test: Error creating user: {e}")

    email, token = login(email="test@email.com", password="password123")
    if email and token:
        auth_logger.info(f"Test: Login exitoso - {email}")
    else:
        auth_logger.warning("Test: Login fallido")
