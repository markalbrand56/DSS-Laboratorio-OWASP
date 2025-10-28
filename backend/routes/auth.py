"""
Rutas de autenticación y gestión de usuarios.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError

from backend.models.responses import SuccessfulLoginResponse, SuccessfulRegisterResponse
from backend.models.user import RegisterRequest, LoginRequest, UpdateUserRequest
from backend.database import db, User, redis_instance
from backend.controllers.auth import (
    login as login_controller,
    register as register_controller,
    get_current_user,
    update as update_controller,
)
from backend.controllers.keys import generate_rsa_keys, generate_ecc_keys
from backend.config.settings import MAX_LOGIN_ATTEMPTS, RATE_LIMIT_WINDOW_SECONDS
from backend.utils.logging_config import auth_logger

router = APIRouter()


# ==================== RATE LIMITING ====================

def _get_client_ip(request: Request) -> str:
    """
    Obtiene la IP real del cliente considerando cabeceras de proxy.
    
    Args:
        request: Request de FastAPI
    
    Returns:
        IP del cliente
    """
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host


def _is_rate_limited(ip: str, email: str) -> bool:
    """
    Verifica si el cliente/email está bloqueado por demasiados intentos fallidos.
    
    Args:
        ip: IP del cliente
        email: Email del usuario
    
    Returns:
        True si está bloqueado, False en caso contrario
    """
    ip_key = f"login:ip:{ip}"
    email_key = f"login:email:{email}"

    ip_attempts = int(redis_instance.get(ip_key) or 0)
    email_attempts = int(redis_instance.get(email_key) or 0)

    is_limited = ip_attempts >= MAX_LOGIN_ATTEMPTS or email_attempts >= MAX_LOGIN_ATTEMPTS
    
    if is_limited:
        auth_logger.warning(f"Rate limit excedido - IP: {ip}, Email: {email}")
    
    return is_limited


def _register_failed_attempt(ip: str, email: str):
    """
    Incrementa contadores en Redis con expiración.
    
    Args:
        ip: IP del cliente
        email: Email del usuario
    """
    ip_key = f"login:ip:{ip}"
    email_key = f"login:email:{email}"

    pipe = redis_instance.pipeline()
    pipe.incr(ip_key)
    pipe.expire(ip_key, RATE_LIMIT_WINDOW_SECONDS)
    pipe.incr(email_key)
    pipe.expire(email_key, RATE_LIMIT_WINDOW_SECONDS)
    pipe.execute()
    
    auth_logger.debug(f"Intento fallido registrado - IP: {ip}, Email: {email}")


def _reset_attempts(ip: str, email: str):
    """
    Elimina contadores al autenticarse exitosamente.
    
    Args:
        ip: IP del cliente
        email: Email del usuario
    """
    redis_instance.delete(f"login:ip:{ip}", f"login:email:{email}")
    auth_logger.debug(f"Intentos reseteados - IP: {ip}, Email: {email}")


# ==================== ENDPOINTS ====================


@router.post("/login", response_model=SuccessfulLoginResponse, status_code=200)
async def login(login_request: LoginRequest, request: Request) -> SuccessfulLoginResponse:
    """
    Endpoint de login con rate limiting.
    
    Args:
        login_request: Credenciales del usuario
        request: Request de FastAPI
    
    Returns:
        Email y token JWT si el login es exitoso
    
    Raises:
        HTTPException: Si hay demasiados intentos o credenciales inválidas
    """
    ip = _get_client_ip(request)
    email = login_request.email

    # Verificar rate limiting
    if _is_rate_limited(ip, email):
        raise HTTPException(
            status_code=429,
            detail="Too many failed login attempts. Please try again later."
        )

    # Intentar login
    user_email, token = login_controller(login_request.email, login_request.password)

    if user_email and token:
        # Login exitoso → resetear contadores
        _reset_attempts(ip, email)
        auth_logger.info(f"Login exitoso desde IP {ip} para {email}")
        return SuccessfulLoginResponse(email=user_email, jwt_token=token)

    # Intento fallido → registrar
    _register_failed_attempt(ip, email)
    auth_logger.warning(f"Login fallido desde IP {ip} para {email}")
    
    raise HTTPException(
        status_code=401,
        detail="Invalid credentials",
    )

@router.post("/register", response_model=SuccessfulRegisterResponse, status_code=201)
async def register(user: LoginRequest) -> SuccessfulRegisterResponse:
    """
    Endpoint de registro de nuevos usuarios.
    
    Args:
        user: Datos del usuario a registrar
    
    Returns:
        Confirmación del registro
    
    Raises:
        HTTPException: Si el usuario ya existe o hay error
    """
    try:
        register_controller(
            email=str(user.email),
            password=user.password,
            name=user.name,
            surname=user.surname,
            birthdate=str(user.birthdate)
        )
        auth_logger.info(f"Usuario registrado: {user.email}")
        
        return SuccessfulRegisterResponse(
            email=str(user.email),
            message="User created successfully",
        )
    except IntegrityError:
        auth_logger.warning(f"Intento de registro duplicado: {user.email}")
        raise HTTPException(
            status_code=409,
            detail="User already exists",
        )
    except Exception as e:
        auth_logger.error(f"Error al registrar {user.email}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Error creating user: {e}",
        )

    


@router.post("/generate-keys")
def generate_keys(user: User = Depends(get_current_user)):
    """
    Genera un par de llaves RSA y ECC para el usuario autenticado.
    
    Args:
        user: Usuario autenticado
    
    Returns:
        Llaves privadas generadas (las públicas se guardan en BD)
    
    Raises:
        HTTPException: Si el usuario no existe o hay error
    """
    try:
        with db.write() as session:
            # Obtener usuario desde la BD
            user_in_db = session.query(User).filter_by(email=user.email).first()

            if not user_in_db:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")

            # Generar llaves RSA
            rsa_private, rsa_public = generate_rsa_keys()
            # Generar llaves ECC
            ecc_private, ecc_public = generate_ecc_keys()

            # Guardar llaves públicas
            user_in_db.public_key_RSA = rsa_public
            user_in_db.public_key_ECC = ecc_public

            session.commit()
            auth_logger.info(f"Llaves generadas para usuario: {user.email}")

            return {
                "message": "Llaves generadas exitosamente.",
                "rsa_private_key": rsa_private,
                "ecc_private_key": ecc_private
            }
    except HTTPException:
        raise
    except Exception as e:
        auth_logger.error(f"Error al generar llaves para {user.email}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al generar llaves: {e}")


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    """
    Obtiene información del usuario autenticado.
    
    Args:
        user: Usuario autenticado
    
    Returns:
        Datos del usuario
    """
    return {
        "email": user.email,
        "name": user.name,
        "surname": user.surname,
        "birthdate": user.birthdate,
    }


@router.put("/me")
async def update_me(update: UpdateUserRequest, user: User = Depends(get_current_user)):
    """
    Actualiza información del usuario autenticado.
    
    Args:
        update: Nuevos datos del usuario
        user: Usuario autenticado
    
    Returns:
        Confirmación de actualización
    
    Raises:
        HTTPException: Si hay error en la actualización
    """
    try:
        update_controller(
            id=user.email,
            email=str(update.email),
            password=update.password,
            name=update.name,
            surname=update.surname,
            birthdate=update.birthdate
        )
        auth_logger.info(f"Usuario actualizado: {user.email}")
        return {"message": "User updated successfully"}
    except Exception as e:
        auth_logger.error(f"Error al actualizar {user.email}: {e}")
        raise HTTPException(status_code=400, detail=f"Error updating user: {e}")


@router.delete("/me")
async def delete_me(user: User = Depends(get_current_user)):
    """
    Elimina el usuario autenticado.
    
    Args:
        user: Usuario autenticado
    
    Returns:
        Confirmación de eliminación
    
    Raises:
        HTTPException: Si el usuario no existe
    """
    try:
        with db.write() as session:
            user_in_db = session.query(User).filter_by(email=user.email).first()
            if not user_in_db:
                raise HTTPException(status_code=404, detail="User not found")
            session.delete(user_in_db)
            session.commit()
            auth_logger.info(f"Usuario eliminado: {user.email}")
            
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        auth_logger.error(f"Error al eliminar {user.email}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting user: {e}")
