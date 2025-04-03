from pydantic import BaseModel

class SuccessfulLoginResponse(BaseModel):
    jwt_token: str
    email: str