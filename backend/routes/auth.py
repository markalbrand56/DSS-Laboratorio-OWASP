from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from backend.models.responses import SuccessfulLoginResponse, SuccessfulRegisterResponse
from backend.models.user import UserBase
from backend.controllers.auth import (
    login as login_controller,
    register as register_controller,
    get_current_user,
)

router = APIRouter()

@router.post("/login", response_model=SuccessfulLoginResponse, status_code=200)
async def login(user: UserBase = Depends(UserBase)) -> SuccessfulLoginResponse:
    """
    Login endpoint to authenticate users.

    It returns a JWT token and the user's email if successful.
    If its the first time the user logs in, it generates a new RSA key pair.
    If the user already has a key pair, it does not generate a new one.
    Keep in mind that the private key is only generated once and is not stored in the database.
    Only the public key is stored in the database.
    """
    u, t, k = login_controller(str(user.email), user.password)

    if u and t:
        return SuccessfulLoginResponse(
            email=u,
            jwt_token=t,
            private_key=k,
        )

    raise HTTPException(
        status_code=401,
        detail="Invalid credentials",
    )


@router.post("/register")
async def register(user: UserBase = Depends(UserBase)):
    """
    Registration endpoint to create a new user.
    """
    try:
        register_controller(user.email, user.password)
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

@router.get("/user")
def read_me(user = Depends(get_current_user)):
    return {"email": user.email, "public_key": user.public_key}
