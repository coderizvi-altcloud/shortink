"""Redis client helpers."""

from functools import lru_cache
from urllib.parse import urlparse, urlunparse

import redis
from redis.exceptions import ConnectionError, RedisError

from backend.source.config.settings.redis_setting import REDIS_URL


class RedisClientProxy:
    def __init__(self, primary: redis.Redis, fallback: redis.Redis | None = None):
        self._primary = primary
        self._fallback = fallback
        self._active = primary

    def _should_fallback(self, error: Exception) -> bool:
        return isinstance(error, (ConnectionError, RedisError)) and self._fallback is not None

    def __getattr__(self, name):
        attr = getattr(self._active, name)
        if not callable(attr):
            return attr

        def wrapper(*args, **kwargs):
            try:
                return attr(*args, **kwargs)
            except Exception as error:
                if self._active is self._primary and self._should_fallback(error):
                    self._active = self._fallback
                    fallback_attr = getattr(self._active, name)
                    return fallback_attr(*args, **kwargs)
                raise

        return wrapper


@lru_cache(maxsize=1)
def get_redis_client() -> RedisClientProxy:
    primary = redis.from_url(REDIS_URL, decode_responses=True)

    fallback = None
    parsed = urlparse(REDIS_URL)
    if parsed.scheme == "rediss":
        fallback_url = urlunparse(parsed._replace(scheme="redis"))
        fallback = redis.from_url(fallback_url, decode_responses=True)

    return RedisClientProxy(primary, fallback)
