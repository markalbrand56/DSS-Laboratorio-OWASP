from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from models.responses import SuccessfulLoginResponse, SuccessfulRegisterResponse
from models.user import RegisterRequest, LoginRequest, UpdateUserRequest  # You need to define this model
from database import db, User
from controllers.auth import (
    login as login_controller,
    register as register_controller,
    get_current_user,
)
from controllers.keys import generate_rsa_keys, generate_ecc_keys

router = APIRouter()

@router.post("/login", response_model=SuccessfulLoginResponse, status_code=200)
async def login(login_request: LoginRequest) -> SuccessfulLoginResponse:
    """
    Login endpoint to authenticate users using query parameters.

    It returns a JWT token and the user's email if successful.
    """
    u, t = login_controller(login_request.email, login_request.password)

    if u and t:
        return SuccessfulLoginResponse(
            email=u,
            jwt_token=t
        )

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
            birthdate=str(user.birthdate)
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
            "ecc_private_key": ecc_private
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
    with db.write() as session:
        user_in_db = session.query(User).filter_by(email=user.email).first()
        if not user_in_db:
            raise HTTPException(status_code=404, detail="User not found")
        if update.name is not None:
            user_in_db.name = update.name
        if update.surname is not None:
            user_in_db.surname = update.surname
        if update.birthdate is not None:
            user_in_db.birthdate = update.birthdate
        session.commit()
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
        session.commit()
        return {"message": "User deleted successfully"}
