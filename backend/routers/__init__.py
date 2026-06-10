from .authrouter import router as auth_router
from .triprouter import router as trip_router
from .generaterouter import router as generate_router

__all__ = ["auth_router", "trip_router", "generate_router"]
