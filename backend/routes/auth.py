from fastapi import APIRouter, Depends, HTTPException

from backend.models.responses import SuccessfulLoginResponse
from backend.models.user import UserBase
from backend.controllers.auth import login as login_controller

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/login", response_model=SuccessfulLoginResponse, status_code=200)
async def login(user: UserBase = Depends(UserBase)) -> SuccessfulLoginResponse:
    """
    Login endpoint to authenticate users.
    """
    u, t = login_controller(user.email, user.password)

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
    # Dummy registration logic
    if user.email and user.password:
        return {"message": "User registered successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid data")
