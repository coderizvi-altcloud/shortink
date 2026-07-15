"""Redis-backed CRUD repository for shortlink records."""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Sequence

from redis import Redis

from backend.source.config.settings.redis_setting import (
    REDIS_CLICK_COUNT_TTL_SECONDS,
    REDIS_SHORTLINK_TTL_SECONDS,
)
from backend.source.utils.base62 import ALPHABET

SHORTLINK_PREFIX = "shortlink"
URL_INDEX_PREFIX = f"{SHORTLINK_PREFIX}:url"
CODE_INDEX_PREFIX = f"{SHORTLINK_PREFIX}:code"
ID_KEY_PREFIX = f"{SHORTLINK_PREFIX}:id"
NEXT_ID_KEY = f"{SHORTLINK_PREFIX}:next_id"
ORDER_KEY = f"{SHORTLINK_PREFIX}:all"
USER_ORDER_PREFIX = f"{SHORTLINK_PREFIX}:user"


@dataclass(slots=True)
class ShortlinkRecord:
    id: int
    short_code: str
    url: str
    user_id: int
    click_count: int = 0
    created_at: str = ""


class ShortlinkRepository:
    """Redis operations for shortlink entities."""

    def _url_key(self, url: str) -> str:
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return f"{URL_INDEX_PREFIX}:{digest}"

    def _code_key(self, short_code: str) -> str:
        return f"{CODE_INDEX_PREFIX}:{short_code}"

    def _id_key(self, shortlink_id: int) -> str:
        return f"{ID_KEY_PREFIX}:{shortlink_id}"

    def _user_order_key(self, user_id: int) -> str:
        return f"{USER_ORDER_PREFIX}:{user_id}"

    def _serialize(self, payload: dict[str, str]) -> ShortlinkRecord:
        return ShortlinkRecord(
            id=int(payload["id"]),
            short_code=payload["short_code"],
            url=payload["url"],
            user_id=int(payload.get("user_id", 0)),
            click_count=int(payload.get("click_count", 0)),
            created_at=payload.get("created_at", ""),
        )

    def _load_by_id(self, redis_client: Redis, shortlink_id: int) -> ShortlinkRecord | None:
        payload = redis_client.hgetall(self._id_key(shortlink_id))
        if not payload:
            return None
        return self._serialize(payload)

    def _load_by_code(self, redis_client: Redis, short_code: str) -> ShortlinkRecord | None:
        shortlink_id = redis_client.get(self._code_key(short_code))
        if shortlink_id is None:
            return None
        return self._load_by_id(redis_client, int(shortlink_id))

    def _generate_short_code(self, length: int = 5) -> str:
        return "".join(secrets.choice(ALPHABET) for _ in range(length))

    def _apply_ttl(self, redis_client: Redis, *keys: str) -> None:
        ttl_values = [value for value in (REDIS_SHORTLINK_TTL_SECONDS, REDIS_CLICK_COUNT_TTL_SECONDS) if value > 0]
        ttl = min(ttl_values) if ttl_values else 0
        if ttl <= 0:
            return
        for key in keys:
            redis_client.expire(key, ttl)

    def create(self, redis_client: Redis, *, url: str, user_id: int) -> ShortlinkRecord:
        short_code = self._generate_short_code()
        while redis_client.exists(self._code_key(short_code)):
            short_code = self._generate_short_code()

        shortlink_id = int(redis_client.incr(NEXT_ID_KEY))
        created_at = datetime.now(timezone.utc).isoformat()
        record = ShortlinkRecord(
            id=shortlink_id,
            short_code=short_code,
            url=url,
            user_id=user_id,
            click_count=0,
            created_at=created_at,
        )

        pipe = redis_client.pipeline()
        pipe.hset(
            self._id_key(shortlink_id),
            mapping={
                "id": str(shortlink_id),
                "short_code": short_code,
                "url": url,
                "user_id": str(user_id),
                "click_count": "0",
                "created_at": created_at,
            },
        )
        pipe.set(self._code_key(short_code), shortlink_id)
        pipe.set(self._url_key(url), shortlink_id)
        pipe.zadd(ORDER_KEY, {str(shortlink_id): shortlink_id})
        pipe.zadd(self._user_order_key(user_id), {str(shortlink_id): shortlink_id})
        pipe.execute()
        self._apply_ttl(
            redis_client,
            self._id_key(shortlink_id),
            self._code_key(short_code),
            self._url_key(url),
            ORDER_KEY,
        )
        return record

    def get_by_id(self, redis_client: Redis, shortlink_id: int) -> ShortlinkRecord | None:
        return self._load_by_id(redis_client, shortlink_id)

    def get_by_url(self, redis_client: Redis, url: str) -> ShortlinkRecord | None:
        shortlink_id = redis_client.get(self._url_key(url))
        if shortlink_id is None:
            return None
        return self._load_by_id(redis_client, int(shortlink_id))

    def get_by_short_code(self, redis_client: Redis, short_code: str) -> ShortlinkRecord | None:
        return self._load_by_code(redis_client, short_code)

    def list_all(self, redis_client: Redis) -> Sequence[ShortlinkRecord]:
        ids = redis_client.zrevrange(ORDER_KEY, 0, -1)
        records: list[ShortlinkRecord] = []
        for value in ids:
            record = self._load_by_id(redis_client, int(value))
            if record is not None:
                records.append(record)
        return records

    def list_by_user(self, redis_client: Redis, user_id: int) -> Sequence[ShortlinkRecord]:
        ids = redis_client.zrevrange(self._user_order_key(user_id), 0, -1)
        records: list[ShortlinkRecord] = []
        for value in ids:
            record = self._load_by_id(redis_client, int(value))
            if record is not None:
                records.append(record)
        return records

    def update(
        self,
        redis_client: Redis,
        shortlink: ShortlinkRecord,
        *,
        url: str | None = None,
        short_code: str | None = None,
    ) -> ShortlinkRecord:
        current_url = shortlink.url
        current_code = shortlink.short_code

        if url is not None and url != current_url:
            redis_client.delete(self._url_key(current_url))
            redis_client.set(self._url_key(url), shortlink.id)
            shortlink.url = url

        if short_code is not None and short_code != current_code:
            if redis_client.exists(self._code_key(short_code)):
                raise ValueError("Short code already exists")
            redis_client.delete(self._code_key(current_code))
            redis_client.set(self._code_key(short_code), shortlink.id)
            shortlink.short_code = short_code

        redis_client.hset(
            self._id_key(shortlink.id),
            mapping={
                "short_code": shortlink.short_code,
                "url": shortlink.url,
            },
        )
        self._apply_ttl(
            redis_client,
            self._id_key(shortlink.id),
            self._code_key(shortlink.short_code),
            self._url_key(shortlink.url),
            ORDER_KEY,
        )
        return shortlink

    def delete(self, redis_client: Redis, shortlink: ShortlinkRecord) -> None:
        pipe = redis_client.pipeline()
        pipe.delete(self._id_key(shortlink.id))
        pipe.delete(self._code_key(shortlink.short_code))
        pipe.delete(self._url_key(shortlink.url))
        pipe.zrem(ORDER_KEY, str(shortlink.id))
        pipe.zrem(self._user_order_key(shortlink.user_id), str(shortlink.id))
        pipe.execute()

    def increment_click_count(self, redis_client: Redis, shortlink: ShortlinkRecord) -> ShortlinkRecord:
        new_count = redis_client.hincrby(self._id_key(shortlink.id), "click_count", 1)
        shortlink.click_count = int(new_count)
        if REDIS_CLICK_COUNT_TTL_SECONDS > 0:
            redis_client.expire(self._id_key(shortlink.id), REDIS_CLICK_COUNT_TTL_SECONDS)
        return shortlink

    def delete_by_id(self, redis_client: Redis, shortlink_id: int) -> bool:
        shortlink = self.get_by_id(redis_client, shortlink_id)
        if shortlink is None:
            return False
        self.delete(redis_client, shortlink)
        return True

    def clear_namespace(self, redis_client: Redis) -> None:
        keys = list(redis_client.scan_iter(f"{SHORTLINK_PREFIX}:*"))
        if keys:
            redis_client.delete(*keys)
