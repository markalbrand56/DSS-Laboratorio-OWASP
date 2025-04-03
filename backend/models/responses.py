from pydantic import BaseModel

class SuccessfulLoginResponse(BaseModel):
    email: str
    jwt_token: str
    private_key: str

class SuccessfulRegisterResponse(BaseModel):
    email: str
    message: str