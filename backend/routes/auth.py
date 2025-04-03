from fastapi import APIRouter, Depends, HTTPException
from backend.models.user import UserBase

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/login")
async def login(user: UserBase = Depends(UserBase)):
    """
    Login endpoint to authenticate users.
    """
    # Dummy authentication logic
    if user.email == "admin@email.com" and user.password == "password":
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

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
