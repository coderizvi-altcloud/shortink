"""Authentication settings loaded from environment."""

import os

_ENVIRONMENT = os.getenv("ENVIRONMENT", "DEV")
_JWT_SECRET_RAW = os.getenv("JWT_SECRET")

if _ENVIRONMENT == "PROD" and not _JWT_SECRET_RAW:
    raise RuntimeError(
        "JWT_SECRET environment variable is required in production. "
        "Set a strong, unique secret before deploying."
    )

# Use dev fallback only in non-production environments
JWT_SECRET = _JWT_SECRET_RAW or "shortink-dev-secret-change-in-production"
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "1440"))  # 24 hours
