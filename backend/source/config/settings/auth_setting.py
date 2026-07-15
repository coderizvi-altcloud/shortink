"""Authentication settings loaded from environment."""

from os import getenv

JWT_SECRET = getenv("JWT_SECRET", "shortink-dev-secret-change-in-production")
JWT_ALGORITHM = getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(getenv("JWT_EXPIRATION_MINUTES", "1440"))  # 24 hours
