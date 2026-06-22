from fastapi import APIRouter, HTTPException, status

from ..models import LoginRequest, RegisterRequest, TokenResponse
from ..security import create_access_token, hash_password, verify_password
from ..store import create_user, get_user, user_exists

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest):
    if len(body.password) < 6:
        raise HTTPException(status_code=422, detail="Password must be at least 6 characters")
    if user_exists(body.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    create_user(body.email, hash_password(body.password))
    return TokenResponse(access_token=create_access_token(body.email))


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    hashed = get_user(body.email)
    if not hashed or not verify_password(body.password, hashed):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(body.email))
