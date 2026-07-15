"""API routes for authentication."""

from fastapi import APIRouter, Depends, HTTPException, status

from backend.source.config import get_redis_client
from backend.source.models.db.user_model import UserRecord, UserRepository
from backend.source.models.schemas.auth_schema import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from backend.source.security.authorizations import get_current_user
from backend.source.security.hashing import hash_password, verify_password
from backend.source.security.verifications import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
userRepository = UserRepository()


def _user_response(user: UserRecord) -> UserResponse:
    return UserResponse(id=user.id, email=user.email, username=user.username)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, redis_client=Depends(get_redis_client)):
    try:
        user = userRepository.create(
            redis_client,
            email=payload.email,
            username=payload.username,
            password_hash=hash_password(payload.password),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    token = create_access_token(user.id)
    return TokenResponse(access_token=token, user=_user_response(user))


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, redis_client=Depends(get_redis_client)):
    user = userRepository.get_by_email(redis_client, payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = create_access_token(user.id)
    return TokenResponse(access_token=token, user=_user_response(user))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserRecord = Depends(get_current_user)):
    return _user_response(current_user)
