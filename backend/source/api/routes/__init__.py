from backend.source.api.routes.auth_routes import router as auth_router
from backend.source.api.routes.shortlink_routes import redirect_router, router as shortlink_router

__all__ = ["auth_router", "redirect_router", "shortlink_router"]
