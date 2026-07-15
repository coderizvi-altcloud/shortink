"""Redis connection settings.

Env is loaded from the project-root `.env` via `backend.source.config.settings`.
"""

from os import getenv

REDIS_URL = getenv("REDIS_URL")
if not REDIS_URL:
    REDIS_HOST = getenv("REDIS_HOST", "localhost")
    REDIS_PORT = getenv("REDIS_PORT", "6379")
    REDIS_USERNAME = getenv("REDIS_USERNAME")
    REDIS_PASSWORD = getenv("REDIS_PASSWORD")
    REDIS_DB = getenv("REDIS_DB", "0")
    REDIS_SCHEME = getenv("REDIS_SCHEME", "rediss")

    if REDIS_USERNAME:
        auth = f"{REDIS_USERNAME}:{REDIS_PASSWORD or ''}"
    elif REDIS_PASSWORD:
        auth = f":{REDIS_PASSWORD}"
    else:
        auth = ""

    REDIS_URL = f"{REDIS_SCHEME}://{auth}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

PUBLIC_BASE_URL = getenv("PUBLIC_BASE_URL", "").rstrip("/")
REDIS_SHORTLINK_TTL_SECONDS = int(getenv("REDIS_SHORTLINK_TTL_SECONDS", "0"))
REDIS_CLICK_COUNT_TTL_SECONDS = int(getenv("REDIS_CLICK_COUNT_TTL_SECONDS", "0"))
