"""FastAPI dependency for JWT-based authorization."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.source.config import get_redis_client
from backend.source.models.db.user_model import UserRecord, UserRepository
from backend.source.security.verifications import decode_access_token

_bearer = HTTPBearer()

userRepository = UserRepository()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    redis_client=Depends(get_redis_client),
) -> UserRecord:
    token = credentials.credentials
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    user = userRepository.get_by_id(redis_client, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
