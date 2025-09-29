from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from typing import Optional
import re

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2, max_length=50)
    surname: str = Field(..., min_length=2, max_length=50)
    birthdate: date = Field(...)

    @field_validator('name', 'surname')
    def no_html_chars(cls, v):
        if re.search(r'[<>]', v):
            raise ValueError("Field cannot contain '<' or '>' characters")
        return v

class UpdateUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: Optional[str] = None
    surname: Optional[str] = None
    birthdate: Optional[str] = None

    @field_validator('name', 'surname')
    def no_html_chars(cls, v):
        if v is not None and re.search(r'[<>]', v):
            raise ValueError("Field cannot contain '<' or '>' characters")
        return v
