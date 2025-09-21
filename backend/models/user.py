from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2, max_length=50)
    surname: str = Field(..., min_length=2, max_length=50)
    birthdate: date = Field(...)

class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    birthdate: Optional[str] = None
