from pydantic import BaseModel

class SuccessfulLoginResponse(BaseModel):
    jwt_token: str
    email: str

class SuccessfulRegisterResponse(BaseModel):
    email: str
    message: str