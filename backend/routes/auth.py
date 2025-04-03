from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from backend.models.responses import SuccessfulLoginResponse, SuccessfulRegisterResponse
from backend.models.user import UserBase
from backend.controllers.auth import (
    login as login_controller,
    register as register_controller,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/login", response_model=SuccessfulLoginResponse, status_code=200)
async def login(user: UserBase = Depends(UserBase)) -> SuccessfulLoginResponse:
    """
    Login endpoint to authenticate users.

    It returns a JWT token and the user's email if successful.
    """
    u, t = login_controller(str(user.email), user.password)

    if u and t:
        return SuccessfulLoginResponse(
            jwt_token=t,
            email=u,
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
