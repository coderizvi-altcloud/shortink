"""Redis-backed user repository."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

from redis import Redis

USER_PREFIX = "user"
USER_ORDER_KEY = f"{USER_PREFIX}:all"
USER_NEXT_ID_KEY = f"{USER_PREFIX}:next_id"
USER_EMAIL_INDEX = f"{USER_PREFIX}:email"
USER_USERNAME_INDEX = f"{USER_PREFIX}:username"


@dataclass(slots=True)
class UserRecord:
    id: int
    email: str
    username: str
    password_hash: str
    created_at: str = ""


class UserRepository:
    """Redis operations for user entities."""

    def _id_key(self, user_id: int) -> str:
        return f"{USER_PREFIX}:id:{user_id}"

    def _email_key(self, email: str) -> str:
        digest = hashlib.sha256(email.lower().encode()).hexdigest()
        return f"{USER_EMAIL_INDEX}:{digest}"

    def _username_key(self, username: str) -> str:
        digest = hashlib.sha256(username.lower().encode()).hexdigest()
        return f"{USER_USERNAME_INDEX}:{digest}"

    def _serialize(self, payload: dict[str, str]) -> UserRecord:
        return UserRecord(
            id=int(payload["id"]),
            email=payload["email"],
            username=payload["username"],
            password_hash=payload["password_hash"],
            created_at=payload.get("created_at", ""),
        )

    def _load_by_id(self, redis_client: Redis, user_id: int) -> UserRecord | None:
        payload = redis_client.hgetall(self._id_key(user_id))
        if not payload:
            return None
        return self._serialize(payload)

    def create(self, redis_client: Redis, *, email: str, username: str, password_hash: str) -> UserRecord:
        if self.get_by_email(redis_client, email) is not None:
            raise ValueError("Email already registered")
        if self.get_by_username(redis_client, username) is not None:
            raise ValueError("Username already taken")

        user_id = int(redis_client.incr(USER_NEXT_ID_KEY))
        created_at = datetime.now(timezone.utc).isoformat()
        record = UserRecord(
            id=user_id,
            email=email.lower(),
            username=username.lower(),
            password_hash=password_hash,
            created_at=created_at,
        )

        pipe = redis_client.pipeline()
        pipe.hset(
            self._id_key(user_id),
            mapping={
                "id": str(user_id),
                "email": record.email,
                "username": record.username,
                "password_hash": password_hash,
                "created_at": created_at,
            },
        )
        pipe.set(self._email_key(record.email), user_id)
        pipe.set(self._username_key(record.username), user_id)
        pipe.zadd(USER_ORDER_KEY, {str(user_id): user_id})
        pipe.execute()
        return record

    def get_by_id(self, redis_client: Redis, user_id: int) -> UserRecord | None:
        return self._load_by_id(redis_client, user_id)

    def get_by_email(self, redis_client: Redis, email: str) -> UserRecord | None:
        user_id = redis_client.get(self._email_key(email.lower()))
        if user_id is None:
            return None
        return self._load_by_id(redis_client, int(user_id))

    def get_by_username(self, redis_client: Redis, username: str) -> UserRecord | None:
        user_id = redis_client.get(self._username_key(username.lower()))
        if user_id is None:
            return None
        return self._load_by_id(redis_client, int(user_id))
