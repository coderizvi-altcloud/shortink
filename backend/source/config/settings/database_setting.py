"""Database connection settings.

Env is loaded from the project-root `.env` via `backend.source.config.settings`.
"""

from os import getenv

POSTGRES_SCHEMA = getenv("POSTGRES_SCHEMA", "postgresql")
POSTGRES_USERNAME = getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = getenv("POSTGRES_HOST")
POSTGRES_PORT = getenv("POSTGRES_PORT")
POSTGRES_DB = getenv("POSTGRES_DB")
POSTGRES_URI = getenv("POSTGRES_URI")
DATABASE_URL = getenv("DATABASE_URL")

if not DATABASE_URL and POSTGRES_URI:
    DATABASE_URL = POSTGRES_URI

if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

if not DATABASE_URL:
    missing = [
        name
        for name, value in (
            ("POSTGRES_USERNAME", POSTGRES_USERNAME),
            ("POSTGRES_PASSWORD", POSTGRES_PASSWORD),
            ("POSTGRES_HOST", POSTGRES_HOST),
            ("POSTGRES_PORT", POSTGRES_PORT),
            ("POSTGRES_DB", POSTGRES_DB),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing database environment variables: {', '.join(missing)}")

    DATABASE_URL = (
        f"{POSTGRES_SCHEMA}+psycopg2://"
        f"{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
