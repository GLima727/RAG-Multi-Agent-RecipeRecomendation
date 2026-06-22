from pydantic import BaseModel


class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RecommendRequest(BaseModel):
    ingredients: str
    dietary_restrictions: list[str] | None = None


class RecommendResponse(BaseModel):
    result: str
