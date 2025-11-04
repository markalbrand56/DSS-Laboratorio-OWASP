from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError

from models.responses import SuccessfulLoginResponse, SuccessfulRegisterResponse
from models.user import (
    RegisterRequest,
    LoginRequest,
    UpdateUserRequest,
)  # You need to define this model
from database import db, User
from controllers.auth import (
    login as login_controller,
    register as register_controller,
    get_current_user,
    update as update_controller,
)
from controllers.keys import generate_rsa_keys, generate_ecc_keys
from database import redis_instance

router = APIRouter()

# Conexión a Redis

MAX_ATTEMPTS = 5
WINDOW_SECONDS = 5 * 60  # 15 minutos


def get_client_ip(request: Request) -> str:
    """Obtiene la IP real del cliente considerando cabeceras."""
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host


def is_rate_limited(ip: str, email: str) -> bool:
    """Verifica si el cliente/email está bloqueado por demasiados intentos fallidos."""
    ip_key = f"login:ip:{ip}"
    email_key = f"login:email:{email}"

    # Revisar si alguno superó el límite
    ip_attempts = int(redis_instance.get(ip_key) or 0)
    email_attempts = int(redis_instance.get(email_key) or 0)

    return ip_attempts >= MAX_ATTEMPTS or email_attempts >= MAX_ATTEMPTS


def register_failed_attempt(ip: str, email: str):
    """Incrementa contadores en Redis con expiración."""
    ip_key = f"login:ip:{ip}"
    email_key = f"login:email:{email}"

    # IP
    pipe = redis_instance.pipeline()
    pipe.incr(ip_key)
    pipe.expire(ip_key, WINDOW_SECONDS)
    # Email
    pipe.incr(email_key)
    pipe.expire(email_key, WINDOW_SECONDS)
    pipe.execute()


def reset_attempts(ip: str, email: str):
    """Elimina contadores al autenticarse exitosamente."""
    redis_instance.delete(f"login:ip:{ip}", f"login:email:{email}")


@router.post("/login", response_model=SuccessfulLoginResponse, status_code=200)
async def login(
    login_request: LoginRequest, request: Request
) -> SuccessfulLoginResponse:
    ip = get_client_ip(request)
    email = login_request.email

    if is_rate_limited(ip, email):
        raise HTTPException(
            status_code=429,
            detail="Too many failed login attempts. Please try again later.",
        )

    u, t = login_controller(login_request.email, login_request.password)

    if u and t:
        # Login exitoso → resetea contadores
        reset_attempts(ip, email)
        return SuccessfulLoginResponse(email=u, jwt_token=t)

    # Intento fallido → registrar
    register_failed_attempt(ip, email)

    raise HTTPException(
        status_code=401,
        detail="Invalid credentials",
    )


@router.post("/register", response_model=SuccessfulRegisterResponse, status_code=201)
async def register(user: RegisterRequest) -> SuccessfulRegisterResponse:
    """
    Registration endpoint to create a new user.
    """
    try:
        register_controller(
            email=str(user.email),
            password=user.password,
            name=user.name,
            surname=user.surname,
            birthdate=str(user.birthdate),
        )
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="User already exists",
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error creating user: {e}",
        )

    return SuccessfulRegisterResponse(
        email=str(user.email),
        message="User created successfully",
    )


@router.post("/generate-keys")
def generate_keys(user: User = Depends(get_current_user)):
    """Genera un par de llaves RSA y ECC para el usuario autenticado."""

    with db.write() as session:
        # Se obtiene el usuario desde la BD
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

        return {
            "message": "Llaves generadas exitosamente.",
            "rsa_private_key": rsa_private,
            "ecc_private_key": ecc_private,
        }


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    """
    Get current authenticated user's info.
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
    Update current authenticated user's info.
    """
    try:
        update_controller(
            id=user.email,
            email=str(update.email),
            password=update.password,
            name=update.name,
            surname=update.surname,
            birthdate=update.birthdate,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating user: {e}")

    return {"message": "User updated successfully"}


@router.delete("/me")
async def delete_me(user: User = Depends(get_current_user)):
    """
    Delete current authenticated user.
    """
    with db.write() as session:
        user_in_db = session.query(User).filter_by(email=user.email).first()
        if not user_in_db:
            raise HTTPException(status_code=404, detail="User not found")
        session.delete(user_in_db)

    return {"message": "User deleted successfully"}
